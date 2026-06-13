from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    is_admin: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}
