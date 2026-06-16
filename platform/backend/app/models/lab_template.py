# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.deployment import Deployment
    from app.models.scheduled_action import ScheduledAction


class LabTemplate(Base):
    __tablename__ = "lab_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)

    container_names: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    images: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    build_contexts: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    start_order: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)

    network_name: Mapped[str] = mapped_column(String(128), nullable=False)
    subnet: Mapped[str] = mapped_column(String(32), nullable=False)
    app_ip: Mapped[str] = mapped_column(String(32), nullable=False)

    exposed_ports: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    access_info: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)

    volume_names: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    env_vars: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    requires_privileged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deployments: Mapped[list["Deployment"]] = relationship(back_populates="lab_template")
    scheduled_actions: Mapped[list["ScheduledAction"]] = relationship(back_populates="lab_template")
