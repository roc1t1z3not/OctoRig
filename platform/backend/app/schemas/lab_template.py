# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DeploymentSummary(BaseModel):
    id: int
    status: str
    started_at: Optional[datetime]

    model_config = {"from_attributes": True}


class LabTemplateResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    category: str
    container_names: list[str]
    images: dict[str, str]
    build_contexts: dict[str, str]
    start_order: list[str]
    network_name: str
    subnet: str
    app_ip: str
    exposed_ports: dict[str, int]
    access_info: list[dict[str, str]]
    volume_names: list[str]
    requires_privileged: bool
    is_active: bool
    current_deployment: Optional[DeploymentSummary] = None

    model_config = {"from_attributes": True}
