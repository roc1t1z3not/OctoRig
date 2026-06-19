# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Renders the `{container_ip}` placeholder used in challenge descriptions and
hints. The registry no longer hardcodes a lab's IP into challenge text (it
can't — each deployment gets its own dynamically allocated address) — instead
content authors write `{container_ip}` and this fills in the viewer's own
live deployment IP, or a "not live" message linking to the lab if they
haven't started it.
"""
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.models.deployment import DeploymentStatus
from app.models.lab_template import LabTemplate
from app.models.user import User

_PLACEHOLDER = "{container_ip}"
_TARGET_SPAN = re.compile(r"`([^`]*)" + re.escape(_PLACEHOLDER) + r"([^`]*)`")


def render_target_text(
    text: Optional[str],
    db: Session,
    current_user: User,
    lab_template_id: Optional[int],
) -> Optional[str]:
    if text is None or _PLACEHOLDER not in text or lab_template_id is None:
        return text

    from app.services.lab_service import get_active_deployment

    template = db.get(LabTemplate, lab_template_id)
    active = get_active_deployment(db, lab_template_id, started_by_id=current_user.id)
    live_ip = active.app_ip if (active and active.status == DeploymentStatus.RUNNING) else None

    def _replace(match: re.Match) -> str:
        prefix, suffix = match.group(1), match.group(2)
        if live_ip:
            return f"`{prefix}{live_ip}{suffix}`"
        if template is not None:
            return f"Not live yet — [start {template.name}](/labs/{template.slug})"
        return "Not live yet"

    return _TARGET_SPAN.sub(_replace, text)


def render_access_info(
    access_info: list[dict[str, str]], app_ip: Optional[str] = None
) -> list[dict[str, str]]:
    if app_ip:
        return [
            {**entry, "value": entry.get("value", "").replace(_PLACEHOLDER, app_ip)}
            for entry in access_info
        ]
    return [
        {**entry, "value": "Not running"} if _PLACEHOLDER in entry.get("value", "") else entry
        for entry in access_info
    ]
