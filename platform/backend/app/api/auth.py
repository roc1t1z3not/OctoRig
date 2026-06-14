from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.api.deps import get_current_user, get_current_user_or_api_key
from app.config import settings
from app.core.exceptions import bad_request, credentials_exception
from app.core.limiter import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services import audit_service
from app.services.audit_service import write_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    ip = request.client.host if request.client else None

    if user is None or not verify_password(payload.password, user.hashed_password):
        write_audit(
            db, action=audit_service.AUTH_LOGIN_FAILED,
            detail={"username": payload.username}, ip=ip,
        )
        raise credentials_exception

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    write_audit(db, action=audit_service.AUTH_LOGIN, user_id=user.id, ip=ip)

    # Ensure every user has a personal team (idempotent)
    from app.services.team_service import ensure_personal_team
    ensure_personal_team(db, user)

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    write_audit(db, action=audit_service.AUTH_LOGOUT, user_id=current_user.id)
    return {"message": "logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user_or_api_key)) -> User:
    return current_user


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password", status_code=204)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise bad_request("Current password is incorrect")
    if len(payload.new_password) < 8:
        raise bad_request("New password must be at least 8 characters")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    write_audit(db, action="auth.password_changed", user_id=current_user.id)
