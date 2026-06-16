from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.team import TeamRole


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_personal: bool
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamWithRole(TeamResponse):
    """Team enriched with the caller's membership role."""
    my_role: TeamRole
    member_count: int


class MemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    username: str
    email: str
    role: TeamRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class InviteRequest(BaseModel):
    username: str
    role: TeamRole = TeamRole.MEMBER


class InvitationResponse(BaseModel):
    id: int
    team_id: int
    email: str
    role: TeamRole
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class InvitationDetail(BaseModel):
    """Public-facing invitation info (no sensitive data)."""
    team_name: str
    team_slug: str
    role: TeamRole
    invited_by_username: str
    expires_at: datetime


class ChangeMemberRoleRequest(BaseModel):
    role: TeamRole


class TransferOwnershipRequest(BaseModel):
    new_owner_id: int
