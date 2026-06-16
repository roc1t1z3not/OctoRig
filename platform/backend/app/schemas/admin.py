# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

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


class SiteSettingsResponse(BaseModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: Optional[str]
    max_flag_attempts: Optional[int]
    dynamic_scoring_enabled: bool
    dynamic_decay_factor: float
    dynamic_min_floor_pct: int
    scoreboard_frozen_at: Optional[datetime]
    first_blood_enabled: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class SiteSettingsUpdate(BaseModel):
    registration_open: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    max_flag_attempts: Optional[int] = Field(None, ge=1)
    dynamic_scoring_enabled: Optional[bool] = None
    dynamic_decay_factor: Optional[float] = Field(None, ge=0.0, le=1.0)
    dynamic_min_floor_pct: Optional[int] = Field(None, ge=1, le=100)
    scoreboard_frozen_at: Optional[datetime] = None
    first_blood_enabled: Optional[bool] = None


class PublicSettingsResponse(BaseModel):
    registration_open: bool
    maintenance_mode: bool
    maintenance_message: Optional[str]
    first_blood_enabled: bool
