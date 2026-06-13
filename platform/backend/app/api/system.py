from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.deployment import Deployment, DeploymentStatus
from app.models.user import User
from app.services.docker_runtime import docker_service

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    docker_ok = docker_service.ping()

    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    running_labs = (
        db.query(Deployment)
        .filter(Deployment.status == DeploymentStatus.RUNNING)
        .count()
    )

    all_containers = docker_service.get_all_octorig_containers()

    return {
        "docker": "ok" if docker_ok else "error",
        "database": "ok" if db_ok else "error",
        "running_labs": running_labs,
        "total_containers": len(all_containers),
    }


@router.get("/containers")
def containers(_: User = Depends(get_current_user)) -> list[dict]:
    """
    All octorig-* containers visible to Docker daemon — includes those
    started by the CLI that have no Deployment row in the database.
    """
    return docker_service.get_all_octorig_containers()


@router.get("/plugins")
def list_plugins(_: User = Depends(get_current_user)) -> list[dict]:
    from app.plugins.registry import list_plugins as _list
    return _list()
