import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from app.core.db_types import EnumCol as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.challenge import Challenge
    from app.models.lab_template import LabTemplate
    from app.models.scheduled_action import ScheduledAction
    from app.models.team import Team
    from app.models.user import User


class DeploymentStatus(str, enum.Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class DeploymentVisibility(str, enum.Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_template_id: Mapped[int] = mapped_column(ForeignKey("lab_templates.id"), nullable=False, index=True)
    started_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    challenge_id: Mapped[Optional[int]] = mapped_column(ForeignKey("challenges.id"), nullable=True, index=True)
    instance_for_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    status: Mapped[DeploymentStatus] = mapped_column(
        SQLEnum(DeploymentStatus), nullable=False, default=DeploymentStatus.STARTING
    )
    visibility: Mapped[DeploymentVisibility] = mapped_column(
        SQLEnum(DeploymentVisibility), nullable=False, default=DeploymentVisibility.PRIVATE
    )

    container_names: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    container_ids: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    dynamic_flag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    auto_destroy_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lab_template: Mapped["LabTemplate"] = relationship(back_populates="deployments")
    user: Mapped["User"] = relationship(
        foreign_keys=[started_by_id], back_populates="deployments"
    )
    team: Mapped[Optional["Team"]] = relationship(back_populates="deployments")
    challenge: Mapped[Optional["Challenge"]] = relationship(back_populates="deployments")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="deployment")
    scheduled_actions: Mapped[list["ScheduledAction"]] = relationship(back_populates="deployment")
