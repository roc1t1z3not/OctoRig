from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.exceptions import bad_request, conflict, not_found
from app.core.security import hash_password
from app.models.api_key import ApiKey
from app.models.audit_log import AuditLog
from app.models.challenge import ChallengeSubmission, HintUnlock
from app.models.deployment import Deployment, DeploymentStatus
from app.models.rank import Rank
from app.models.scheduled_action import ScheduledAction, ScheduledActionStatus
from app.models.scoring import ScoreTransaction
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.admin import (
    AdminApiKeyResponse,
    AdminAuditLogResponse,
    AdminResetPassword,
    AdminTeamResponse,
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    SiteSettingsResponse,
    SiteSettingsUpdate,
    SystemStats,
)
from app.services import api_key_service, audit_service
from app.services.settings_service import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=SystemStats)
def get_stats(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SystemStats:
    active_statuses = [DeploymentStatus.STARTING, DeploymentStatus.RUNNING]
    return SystemStats(
        user_count=db.query(User).count(),
        team_count=db.query(Team).filter(Team.is_personal.is_(False)).count(),
        active_deployments=db.query(Deployment).filter(Deployment.status.in_(active_statuses)).count(),
        total_deployments=db.query(Deployment).count(),
        api_key_count=db.query(ApiKey).filter(ApiKey.is_active.is_(True)).count(),
        pending_scheduled_actions=db.query(ScheduledAction)
            .filter(ScheduledAction.status == ScheduledActionStatus.PENDING)
            .count(),
    )


# ── Users ────────────────────────────────────────────────────────────────────

def _enrich_user(user: User, db: Session) -> AdminUserResponse:
    team_count = db.query(TeamMember).filter(TeamMember.user_id == user.id).count()
    deployment_count = db.query(Deployment).filter(Deployment.started_by_id == user.id).count()
    api_key_count = db.query(ApiKey).filter(ApiKey.user_id == user.id, ApiKey.is_active.is_(True)).count()
    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        team_count=team_count,
        deployment_count=deployment_count,
        api_key_count=api_key_count,
    )


@router.get("/users/", response_model=list[AdminUserResponse])
def list_users(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter((User.username.ilike(like)) | (User.email.ilike(like)))
    users = q.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return [_enrich_user(u, db) for u in users]


@router.post("/users/", response_model=AdminUserResponse, status_code=201)
def create_user(
    payload: AdminUserCreate,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    if db.query(User).filter(User.username == payload.username).first():
        raise conflict(f"Username '{payload.username}' is already taken")
    if db.query(User).filter(User.email == payload.email).first():
        raise conflict(f"Email '{payload.email}' is already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_admin=payload.is_admin,
        is_superuser=payload.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.team_service import ensure_personal_team
    ensure_personal_team(db, user)

    audit_service.write_audit(
        db, action=audit_service.ADMIN_USER_CREATED, user_id=actor.id,
        detail={"created_username": payload.username},
        ip=request.client.host if request.client else None,
    )
    return _enrich_user(user, db)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("User")
    return _enrich_user(user, db)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("User")
    if user.id == actor.id and payload.is_active is False:
        raise bad_request("Cannot deactivate your own account")

    changes: dict = {}
    if payload.is_active is not None:
        user.is_active = payload.is_active
        changes["is_active"] = payload.is_active
    if payload.is_admin is not None and actor.is_superuser:
        user.is_admin = payload.is_admin
        changes["is_admin"] = payload.is_admin
    if payload.is_superuser is not None and actor.is_superuser:
        user.is_superuser = payload.is_superuser
        changes["is_superuser"] = payload.is_superuser

    db.commit()
    audit_service.write_audit(
        db, action=audit_service.ADMIN_ROLE_CHANGED, user_id=actor.id,
        detail={"target_user_id": user_id, "changes": changes},
        ip=request.client.host if request.client else None,
    )
    return _enrich_user(user, db)


@router.post("/users/{user_id}/reset-password", status_code=204)
def reset_password(
    user_id: int,
    payload: AdminResetPassword,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("User")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    audit_service.write_audit(
        db, action="admin.password_reset", user_id=actor.id,
        detail={"target_user_id": user_id},
        ip=request.client.host if request.client else None,
    )


@router.post("/users/{user_id}/reset-points", status_code=204)
def reset_user_points(
    user_id: int,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("User")
    db.query(ScoreTransaction).filter(ScoreTransaction.user_id == user_id).delete()
    db.query(ChallengeSubmission).filter(ChallengeSubmission.user_id == user_id).delete()
    db.query(HintUnlock).filter(HintUnlock.user_id == user_id).delete()
    db.commit()
    audit_service.write_audit(
        db, action="admin.reset_points", user_id=actor.id,
        detail={"target_user_id": user_id},
        ip=request.client.host if request.client else None,
    )


@router.post("/reset-db", status_code=204)
def reset_database(
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    """Wipe all user-generated data, keeping accounts, teams, labs and challenges."""
    db.query(ScoreTransaction).delete()
    db.query(ChallengeSubmission).delete()
    db.query(HintUnlock).delete()
    db.query(AuditLog).delete()
    db.query(Deployment).delete()
    db.query(ScheduledAction).delete()
    db.commit()
    audit_service.write_audit(
        db, action="admin.reset_db", user_id=actor.id,
        detail={"triggered_by": actor.username},
        ip=request.client.host if request.client else None,
    )


# ── Teams ────────────────────────────────────────────────────────────────────

@router.get("/teams/", response_model=list[AdminTeamResponse])
def list_teams(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminTeamResponse]:
    q = db.query(Team)
    if search:
        q = q.filter(Team.name.ilike(f"%{search}%"))
    teams = q.order_by(Team.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for team in teams:
        creator = db.get(User, team.created_by_id)
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        deployment_count = db.query(Deployment).filter(Deployment.team_id == team.id).count()
        result.append(
            AdminTeamResponse(
                id=team.id,
                name=team.name,
                slug=team.slug,
                is_personal=team.is_personal,
                created_by_id=team.created_by_id,
                created_by_username=creator.username if creator else "unknown",
                member_count=member_count,
                deployment_count=deployment_count,
                created_at=team.created_at,
            )
        )
    return result


# ── Deployments (all) ────────────────────────────────────────────────────────

@router.get("/deployments/", response_model=list[dict])
def list_all_deployments(
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    team_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[dict]:
    from app.api.deployments import _to_response
    q = db.query(Deployment)
    if status:
        q = q.filter(Deployment.status == status)
    if user_id:
        q = q.filter(Deployment.started_by_id == user_id)
    if team_id:
        q = q.filter(Deployment.team_id == team_id)
    deployments = q.order_by(Deployment.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_response(d, db).model_dump() for d in deployments]


# ── Audit logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs/", response_model=list[AdminAuditLogResponse])
def list_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    team_id: Optional[int] = Query(None),
    from_dt: Optional[str] = Query(None, alias="from"),
    to_dt: Optional[str] = Query(None, alias="to"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminAuditLogResponse]:
    from datetime import datetime
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if team_id:
        q = q.filter(AuditLog.team_id == team_id)
    if from_dt:
        q = q.filter(AuditLog.created_at >= datetime.fromisoformat(from_dt))
    if to_dt:
        q = q.filter(AuditLog.created_at <= datetime.fromisoformat(to_dt))

    logs = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for log in logs:
        user = db.get(User, log.user_id) if log.user_id else None
        team = db.get(Team, log.team_id) if log.team_id else None
        result.append(
            AdminAuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                username=user.username if user else None,
                team_id=log.team_id,
                team_name=team.name if team else None,
                deployment_id=log.deployment_id,
                action=log.action,
                detail=log.detail,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
        )
    return result


# ── API Keys (all) ───────────────────────────────────────────────────────────

@router.get("/api-keys/", response_model=list[AdminApiKeyResponse])
def list_all_api_keys(
    user_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminApiKeyResponse]:
    q = db.query(ApiKey)
    if active_only:
        q = q.filter(ApiKey.is_active.is_(True))
    if user_id:
        q = q.filter(ApiKey.user_id == user_id)
    keys = q.order_by(ApiKey.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for key in keys:
        user = db.get(User, key.user_id)
        result.append(
            AdminApiKeyResponse(
                id=key.id,
                user_id=key.user_id,
                username=user.username if user else "unknown",
                name=key.name,
                key_prefix=key.key_prefix,
                expires_at=key.expires_at,
                last_used_at=key.last_used_at,
                is_active=key.is_active,
                created_at=key.created_at,
            )
        )
    return result


# ── Ranks ─────────────────────────────────────────────────────────────────────

class AdminRankResponse(BaseModel):
    id: int
    name: str
    min_points: int
    icon: Optional[str]
    color: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class AdminRankCreate(BaseModel):
    name: str
    min_points: int
    icon: Optional[str] = None
    color: Optional[str] = None


class AdminRankUpdate(BaseModel):
    name: Optional[str] = None
    min_points: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/ranks/", response_model=list[AdminRankResponse])
def list_ranks(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminRankResponse]:
    ranks = db.query(Rank).order_by(Rank.min_points.asc()).all()
    return [AdminRankResponse.model_validate(r) for r in ranks]


@router.post("/ranks/", response_model=AdminRankResponse)
def create_rank(
    body: AdminRankCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminRankResponse:
    if db.query(Rank).filter(Rank.name == body.name).first():
        raise conflict("A rank with that name already exists")
    if db.query(Rank).filter(Rank.min_points == body.min_points).first():
        raise conflict("A rank with that min_points value already exists")
    rank = Rank(
        name=body.name,
        min_points=body.min_points,
        icon=body.icon,
        color=body.color,
    )
    db.add(rank)
    db.commit()
    db.refresh(rank)
    return AdminRankResponse.model_validate(rank)


@router.patch("/ranks/{rank_id}", response_model=AdminRankResponse)
def update_rank(
    rank_id: int,
    body: AdminRankUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminRankResponse:
    rank = db.get(Rank, rank_id)
    if rank is None:
        raise not_found("Rank")
    if body.name is not None:
        existing = db.query(Rank).filter(Rank.name == body.name, Rank.id != rank_id).first()
        if existing:
            raise conflict("A rank with that name already exists")
        rank.name = body.name
    if body.min_points is not None:
        existing = db.query(Rank).filter(
            Rank.min_points == body.min_points, Rank.id != rank_id
        ).first()
        if existing:
            raise conflict("A rank with that min_points value already exists")
        rank.min_points = body.min_points
    if body.icon is not None:
        rank.icon = body.icon
    if body.color is not None:
        rank.color = body.color
    if body.is_active is not None:
        rank.is_active = body.is_active
    db.commit()
    db.refresh(rank)
    return AdminRankResponse.model_validate(rank)


@router.delete("/ranks/{rank_id}", response_model=dict)
def delete_rank(
    rank_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    rank = db.get(Rank, rank_id)
    if rank is None:
        raise not_found("Rank")
    db.delete(rank)
    db.commit()
    return {"deleted": True, "rank_id": rank_id}


# ── Site settings ─────────────────────────────────────────────────────────────

@router.get("/settings", response_model=SiteSettingsResponse)
def get_site_settings(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SiteSettingsResponse:
    return SiteSettingsResponse.model_validate(get_settings(db))


@router.patch("/settings", response_model=SiteSettingsResponse)
def update_site_settings(
    body: SiteSettingsUpdate,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SiteSettingsResponse:
    row = get_settings(db)
    changed: dict = {}
    for field, value in body.model_dump(exclude_none=True).items():
        if getattr(row, field) != value:
            setattr(row, field, value)
            changed[field] = value
    if changed:
        db.commit()
        db.refresh(row)
        audit_service.write_audit(
            db, action="admin.settings_updated", user_id=actor.id,
            detail=changed,
            ip=request.client.host if request.client else None,
        )
    return SiteSettingsResponse.model_validate(row)


# ── API Keys admin revoke ─────────────────────────────────────────────────────

@router.delete("/api-keys/{key_id}", status_code=204)
def admin_revoke_api_key(
    key_id: int,
    request: Request,
    actor: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    api_key_service.revoke_api_key(db, actor, key_id)
    audit_service.write_audit(
        db, action="admin.api_key_revoked", user_id=actor.id,
        detail={"key_id": key_id},
        ip=request.client.host if request.client else None,
    )
