from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    in_app: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    discord_webhook_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    slack_webhook_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    event_filter: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="notification_preferences")
