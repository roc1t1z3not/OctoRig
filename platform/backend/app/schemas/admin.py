from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.deployment import DeploymentStatus, DeploymentVisibility
from app.models.scheduled_action import ScheduledActionStatus, ScheduledActionType


class SystemStats(BaseModel):
    user_count: int
    team_count: int
    active_deployments: int
    total_deployments: int
    api_key_count: int
    pending_scheduled_actions: int


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    is_admin: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    team_count: int
    deployment_count: int
    api_key_count: int

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False
    is_superuser: bool = False


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_superuser: Optional[bool] = None


class AdminResetPassword(BaseModel):
    new_password: str


class AdminTeamResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_personal: bool
    created_by_id: int
    created_by_username: str
    member_count: int
    deployment_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminAuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    team_id: Optional[int]
    team_name: Optional[str]
    deployment_id: Optional[int]
    action: str
    detail: dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminApiKeyResponse(BaseModel):
    id: int
    user_id: int
    username: str
    name: str
    key_prefix: str
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    created_at: datetime
