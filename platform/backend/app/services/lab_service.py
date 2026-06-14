"""
LabService — orchestrates the lab registry, Docker runtime, and database.

start_lab() and stop_lab() are called from BackgroundTasks so they run
after the HTTP response has been sent. They must open their own DB session.
"""
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.labs.registry import LAB_REGISTRY, LabDefinition, REGISTRY_BY_ID
from app.models.deployment import Deployment, DeploymentStatus
from app.models.lab_template import LabTemplate
from app.services.audit_service import write_audit
from app.services.docker_runtime import docker_service
from app.ws.manager import emit as ws_emit


# ------------------------------------------------------------------ #
# Registry sync                                                        #
# ------------------------------------------------------------------ #

def sync_registry(db: Session) -> None:
    """
    Upsert all LabTemplate rows from the Python registry.
    For labs that define inline challenges, also upsert those into the
    challenges / challenge_flags / challenge_hints tables.
    """
    from app.models.challenge import Challenge, ChallengeFlag, ChallengeHint

    for lab_def in LAB_REGISTRY:
        existing = db.query(LabTemplate).filter(LabTemplate.id == lab_def["id"]).first()
        if existing is None:
            template = LabTemplate(
                id=lab_def["id"],
                slug=lab_def["slug"],
                name=lab_def["name"],
                description=lab_def["description"],
                category=lab_def["category"],
                container_names=lab_def["container_names"],
                images=lab_def["images"],
                build_contexts=lab_def["build_contexts"],
                start_order=lab_def["start_order"],
                network_name=lab_def["network_name"],
                subnet=lab_def["subnet"],
                app_ip=lab_def["app_ip"],
                exposed_ports=lab_def["exposed_ports"],
                access_info=lab_def["access_info"],
                volume_names=lab_def["volume_names"],
                env_vars=lab_def["env_vars"],
                requires_privileged=lab_def["requires_privileged"],
            )
            db.add(template)
        else:
            existing.name = lab_def["name"]
            existing.description = lab_def["description"]
            existing.category = lab_def["category"]
            existing.container_names = lab_def["container_names"]
            existing.images = lab_def["images"]
            existing.build_contexts = lab_def["build_contexts"]
            existing.start_order = lab_def["start_order"]
            existing.network_name = lab_def["network_name"]
            existing.subnet = lab_def["subnet"]
            existing.app_ip = lab_def["app_ip"]
            existing.exposed_ports = lab_def["exposed_ports"]
            existing.access_info = lab_def["access_info"]
            existing.volume_names = lab_def["volume_names"]
            existing.env_vars = lab_def["env_vars"]
            existing.requires_privileged = lab_def["requires_privileged"]

        # Sync inline challenges if present
        for ch_def in lab_def.get("challenges", []):
            ch = db.query(Challenge).filter(Challenge.slug == ch_def["slug"]).first()
            if ch is None:
                lab_name_tag = lab_def["name"]
                raw_tags = [t for t in ch_def.get("tags", []) if t != lab_name_tag]
                ch = Challenge(
                    slug=ch_def["slug"],
                    title=ch_def["title"],
                    description=ch_def["description"],
                    challenge_type=ch_def["challenge_type"],
                    difficulty=ch_def["difficulty"],
                    category=ch_def["category"],
                    tags=[lab_name_tag] + raw_tags,
                    skills=ch_def.get("skills", []),
                    points=ch_def.get("points", 100),
                    is_active=True,
                    is_archived=False,
                    lab_template_id=lab_def["id"],
                )
                db.add(ch)
                db.flush()

                for f in ch_def.get("flags", []):
                    db.add(ChallengeFlag(
                        challenge_id=ch.id,
                        value=f["value"],
                        flag_type=f.get("flag_type", "static"),
                        case_sensitive=f.get("case_sensitive", False),
                    ))

                for h in ch_def.get("hints", []):
                    db.add(ChallengeHint(
                        challenge_id=ch.id,
                        order_num=h["order_num"],
                        content=h["content"],
                        cost=h.get("cost", 0),
                    ))
            else:
                # Keep title/description/points in sync if the registry changes
                lab_name_tag = lab_def["name"]
                raw_tags = [t for t in ch_def.get("tags", ch.tags) if t != lab_name_tag]
                ch.title = ch_def["title"]
                ch.description = ch_def["description"]
                ch.points = ch_def.get("points", ch.points)
                ch.tags = [lab_name_tag] + raw_tags
                ch.skills = ch_def.get("skills", ch.skills)
                ch.lab_template_id = lab_def["id"]

    db.commit()


# ------------------------------------------------------------------ #
# Active deployment lookup                                             #
# ------------------------------------------------------------------ #

def get_active_deployment(db: Session, lab_template_id: int) -> Optional[Deployment]:
    return (
        db.query(Deployment)
        .filter(
            Deployment.lab_template_id == lab_template_id,
            Deployment.status.in_([DeploymentStatus.STARTING, DeploymentStatus.RUNNING]),
        )
        .first()
    )


# ------------------------------------------------------------------ #
# Lab lifecycle — called as BackgroundTasks                           #
# ------------------------------------------------------------------ #

def start_lab(deployment_id: int, user_id: int) -> None:
    """
    Full lab start sequence. Runs in a background thread after 202 is sent.
    Opens its own DB session to avoid closed-session issues.
    """
    db = SessionLocal()
    try:
        deployment = db.get(Deployment, deployment_id)
        if deployment is None:
            return

        template = db.get(LabTemplate, deployment.lab_template_id)
        if template is None:
            _fail(db, deployment, "Lab template not found")
            return

        lab_def = REGISTRY_BY_ID.get(template.id)
        if lab_def is None:
            _fail(db, deployment, "Lab definition missing from registry")
            return

        try:
            _do_start(db, deployment, template, lab_def)
        except Exception as exc:
            _fail(db, deployment, str(exc))
            write_audit(
                db,
                action="lab.start.error",
                user_id=user_id,
                deployment_id=deployment_id,
                detail={"error": str(exc), "lab": template.slug},
            )
    finally:
        db.close()


def _do_start(db: Session, deployment: Deployment, template: LabTemplate, lab_def: LabDefinition) -> None:
    # 1. Build images for roles that have a build context
    repo_root = os.path.dirname(settings.labs_root)  # /octorig
    for role, rel_path in lab_def["build_contexts"].items():
        image_tag = lab_def["images"][role]
        context_path = os.path.join(repo_root, rel_path)
        docker_service.build_image(tag=image_tag, context_path=context_path)

    # 2. Pull images for roles without a build context
    for role, image_tag in lab_def["images"].items():
        if role not in lab_def["build_contexts"]:
            docker_service.pull_image(image_tag)

    # 3. Create volumes
    for vol_name in lab_def["volume_names"]:
        docker_service.ensure_volume(vol_name)

    # 4. Create network
    docker_service.ensure_network(lab_def["network_name"], lab_def["subnet"])

    # 5. Generate dynamic flag if this is a challenge-linked deployment
    dynamic_flag: Optional[str] = None
    if deployment.challenge_id is not None:
        challenge_slug = _get_challenge_slug(db, deployment.challenge_id)
        dynamic_flag = f"FLAG{{{challenge_slug}_{uuid.uuid4().hex[:12]}}}"
        deployment.dynamic_flag = dynamic_flag
        db.flush()

    # 5b. Start containers in declared order
    container_ids: dict[str, str] = {}
    subnet_prefix = lab_def["subnet"].rsplit(".", 1)[0]  # e.g. "172.28.8"

    for i, role in enumerate(lab_def["start_order"]):
        container_name = _container_name_for_role(lab_def, role)
        image_tag = lab_def["images"][role]

        # Assign fixed IPs: .2 for first container (app), .3 for db, .4 for pg, etc.
        ip = f"{subnet_prefix}.{i + 2}"

        # Build volume mounts for this container
        volumes = _volumes_for_role(lab_def, role)

        base_env = lab_def["env_vars"] if role == "app" else _db_env_for_role(lab_def, role)
        if role == "app" and dynamic_flag:
            base_env = {**base_env, "CHALLENGE_FLAG": dynamic_flag}

        cid = docker_service.run_container(
            name=container_name,
            image=image_tag,
            network=lab_def["network_name"],
            ip=ip,
            environment=base_env,
            volumes=volumes,
            privileged=lab_def["requires_privileged"],
        )
        container_ids[role] = cid

        # Brief pause to let DB containers initialize before the app starts
        if role in ("db", "pg", "redis"):
            time.sleep(5)

    # 6. Wait for all containers to report 'running'
    all_names = _all_container_names(lab_def)
    deadline = time.time() + 120
    while time.time() < deadline:
        if all(docker_service.get_container_status(n) == "running" for n in all_names):
            break
        time.sleep(2)

    # 7. For fire-ranges, additionally poll /health endpoint
    if template.category == "firerange":
        _wait_for_health(lab_def["app_ip"])

    # 8. VulnAD post-start exec
    if template.slug == "vulnad":
        docker_service.exec_in_container("octorig-vulnad", "/usr/local/bin/_populate_ad")

    # 9. Mark running
    deployment.status = DeploymentStatus.RUNNING
    deployment.container_ids = container_ids
    deployment.started_at = datetime.now(timezone.utc)
    db.commit()

    ws_emit("deployment.update", {
        "id": deployment.id,
        "lab_template_id": template.id,
        "lab_name": template.name,
        "status": "running",
    })

    write_audit(
        db,
        action="lab.start",
        user_id=deployment.started_by_id,
        deployment_id=deployment.id,
        detail={"lab": template.slug, "container_ids": container_ids},
    )


def stop_lab(deployment_id: int, user_id: int, remove_volumes: bool = False) -> None:
    """Stop all containers for a deployment. Runs as a BackgroundTask."""
    db = SessionLocal()
    try:
        deployment = db.get(Deployment, deployment_id)
        if deployment is None:
            return

        template = db.get(LabTemplate, deployment.lab_template_id)
        if template is None:
            return

        lab_def = REGISTRY_BY_ID.get(template.id)

        # Stop containers
        for name in deployment.container_names:
            docker_service.stop_container(name)

        # Remove network
        if lab_def:
            docker_service.remove_network(lab_def["network_name"])
            if remove_volumes:
                for vol in lab_def["volume_names"]:
                    docker_service.remove_volume(vol)

        deployment.status = DeploymentStatus.STOPPED
        deployment.stopped_at = datetime.now(timezone.utc)
        db.commit()

        ws_emit("deployment.update", {
            "id": deployment.id,
            "lab_template_id": template.id if template else None,
            "lab_name": template.name if template else None,
            "status": "stopped",
        })

        write_audit(
            db,
            action="lab.stop",
            user_id=user_id,
            deployment_id=deployment_id,
            detail={"lab": template.slug, "remove_volumes": remove_volumes},
        )
    except Exception as exc:
        if deployment:
            deployment.error_message = str(exc)
            deployment.status = DeploymentStatus.ERROR
            db.commit()
    finally:
        db.close()


def reset_lab(deployment_id: int, user_id: int) -> None:
    """
    Fire-range reset: stop the lab (removing score volumes), then start fresh.
    Creates a new Deployment row for the fresh start.
    """
    db = SessionLocal()
    try:
        old_deployment = db.get(Deployment, deployment_id)
        if old_deployment is None:
            return
        template_id = old_deployment.lab_template_id

        # Stop and remove volumes
        stop_lab(deployment_id, user_id, remove_volumes=True)

        # Create a new deployment and start
        new_deployment = Deployment(
            lab_template_id=template_id,
            started_by_id=user_id,
            status=DeploymentStatus.STARTING,
            container_names=old_deployment.container_names,
        )
        db.add(new_deployment)
        db.commit()
        db.refresh(new_deployment)

        write_audit(
            db,
            action="lab.reset",
            user_id=user_id,
            deployment_id=new_deployment.id,
            detail={"lab_template_id": template_id},
        )
    finally:
        db.close()

    start_lab(new_deployment.id, user_id)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _get_challenge_slug(db: Session, challenge_id: int) -> str:
    from app.models.challenge import Challenge
    ch = db.get(Challenge, challenge_id)
    return ch.slug if ch else str(challenge_id)


def _fail(db: Session, deployment: Deployment, message: str) -> None:
    deployment.status = DeploymentStatus.ERROR
    deployment.error_message = message
    db.commit()
    ws_emit("deployment.update", {
        "id": deployment.id,
        "lab_template_id": deployment.lab_template_id,
        "status": "error",
        "error_message": message,
    })


def _container_name_for_role(lab_def: LabDefinition, role: str) -> str:
    """Pick the right container name from container_names by matching role suffix."""
    names = lab_def["container_names"]
    if len(names) == 1:
        return names[0]
    for name in names:
        if name.endswith(f"-{role}"):
            return name
    # Fallback: use positional index from start_order
    idx = lab_def["start_order"].index(role)
    return names[idx]


def _all_container_names(lab_def: LabDefinition) -> list[str]:
    return lab_def["container_names"]


def _volumes_for_role(lab_def: LabDefinition, role: str) -> dict[str, dict[str, str]]:
    """Mount score volumes only on the app container."""
    if role != "app":
        return {}
    return {vol: {"bind": f"/data/{vol}", "mode": "rw"} for vol in lab_def["volume_names"]}


def _db_env_for_role(lab_def: LabDefinition, role: str) -> dict[str, str]:
    """
    For DB containers (mysql, postgres, redis), extract their specific env vars.
    The lab_def env_vars are written for the app container; DB containers need
    their own MYSQL_ROOT_PASSWORD / POSTGRES_PASSWORD etc.
    """
    env = lab_def["env_vars"]
    if role == "db":
        return {
            "MYSQL_ROOT_PASSWORD": env.get("MYSQL_PASSWORD", "firerange"),
            "MYSQL_DATABASE": env.get("MYSQL_DATABASE", "firerange"),
            "MYSQL_USER": env.get("MYSQL_USER", "firerange"),
            "MYSQL_PASSWORD": env.get("MYSQL_PASSWORD", "firerange"),
        }
    if role == "pg":
        return {
            "POSTGRES_DB": env.get("PG_DATABASE", "firerange"),
            "POSTGRES_USER": env.get("PG_USER", "firerange"),
            "POSTGRES_PASSWORD": env.get("PG_PASSWORD", "firerange"),
        }
    if role == "redis":
        return {}
    return {}


def _wait_for_health(app_ip: str, timeout: int = 60) -> None:
    url = f"http://{app_ip}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = httpx.get(url, timeout=3)
            if resp.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
