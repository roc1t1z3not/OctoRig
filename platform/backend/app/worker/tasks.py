"""
Celery tasks for scheduled lab actions.

dispatch_due_actions: runs every 60s via Celery beat, picks up pending
ScheduledAction rows whose scheduled_at has passed, and fires the appropriate task.

auto_destroy_dynamic_labs: runs every 60s via Celery beat, destroys dynamic
lab deployments that have passed their auto_destroy_at timestamp.
"""
from datetime import datetime, timezone

from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.dispatch_due_actions")
def dispatch_due_actions() -> None:
    from app.database import SessionLocal
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        due = (
            db.query(ScheduledAction)
            .filter(
                ScheduledAction.status == ScheduledActionStatus.PENDING,
                ScheduledAction.scheduled_at <= now,
            )
            .all()
        )
        for action in due:
            action.status = ScheduledActionStatus.EXECUTING
            db.commit()
            if action.action.value == "destroy" and action.deployment_id:
                execute_destroy.delay(action.id)
            elif action.action.value == "deploy" and action.lab_template_id:
                execute_deploy.delay(action.id)
            else:
                action.status = ScheduledActionStatus.FAILED
                action.error_message = "Missing target (deployment_id or lab_template_id)"
                action.executed_at = now
                db.commit()
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.execute_destroy", bind=True, max_retries=2)
def execute_destroy(self, scheduled_action_id: int) -> None:
    from app.database import SessionLocal
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
    from app.services import audit_service, lab_service

    db = SessionLocal()
    try:
        action = db.get(ScheduledAction, scheduled_action_id)
        if action is None:
            return

        now = datetime.now(timezone.utc)
        try:
            lab_service.stop_lab(action.deployment_id, action.user_id)
            action.status = ScheduledActionStatus.COMPLETED
            action.executed_at = now
            db.commit()
            audit_service.write_audit(
                db,
                action=audit_service.SCHEDULE_EXECUTED,
                user_id=action.user_id,
                team_id=action.team_id,
                deployment_id=action.deployment_id,
                detail={"scheduled_action_id": scheduled_action_id, "action": "destroy"},
            )
        except Exception as exc:
            action.status = ScheduledActionStatus.FAILED
            action.error_message = str(exc)
            action.executed_at = now
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.execute_deploy", bind=True, max_retries=2)
def execute_deploy(self, scheduled_action_id: int) -> None:
    from app.database import SessionLocal
    from app.models.deployment import Deployment, DeploymentStatus
    from app.models.lab_template import LabTemplate
    from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
    from app.services import audit_service, lab_service

    db = SessionLocal()
    try:
        action = db.get(ScheduledAction, scheduled_action_id)
        if action is None:
            return

        now = datetime.now(timezone.utc)
        try:
            template = db.get(LabTemplate, action.lab_template_id)
            if template is None:
                raise ValueError("Lab template not found")

            existing = lab_service.get_active_deployment(db, template.id)
            if existing:
                raise ValueError(f"Lab already has an active deployment (id={existing.id})")

            deployment = Deployment(
                lab_template_id=template.id,
                started_by_id=action.user_id,
                team_id=action.team_id,
                status=DeploymentStatus.STARTING,
                container_names=template.container_names,
            )
            db.add(deployment)
            db.commit()
            db.refresh(deployment)

            action.deployment_id = deployment.id
            action.status = ScheduledActionStatus.COMPLETED
            action.executed_at = now
            db.commit()

            lab_service.start_lab(deployment.id, action.user_id)

            audit_service.write_audit(
                db,
                action=audit_service.SCHEDULE_EXECUTED,
                user_id=action.user_id,
                team_id=action.team_id,
                deployment_id=deployment.id,
                detail={"scheduled_action_id": scheduled_action_id, "action": "deploy"},
            )
        except Exception as exc:
            action.status = ScheduledActionStatus.FAILED
            action.error_message = str(exc)
            action.executed_at = now
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.auto_destroy_dynamic_labs")
def auto_destroy_dynamic_labs() -> None:
    """Destroy dynamic lab deployments that have passed their auto_destroy_at timestamp."""
    from app.database import SessionLocal
    from app.models.deployment import Deployment, DeploymentStatus
    from app.services import lab_service

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        expired = (
            db.query(Deployment)
            .filter(
                Deployment.dynamic_flag.isnot(None),
                Deployment.auto_destroy_at.isnot(None),
                Deployment.auto_destroy_at <= now,
                Deployment.status == DeploymentStatus.RUNNING,
            )
            .all()
        )
        for deployment in expired:
            lab_service.stop_lab(deployment.id, deployment.started_by_id)
    finally:
        db.close()
