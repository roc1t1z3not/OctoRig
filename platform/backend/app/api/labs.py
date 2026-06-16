# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import not_found
from app.models.deployment import DeploymentStatus
from app.models.lab_template import LabTemplate
from app.models.user import User
from app.schemas.lab_template import DeploymentSummary, LabTemplateResponse
from app.services.lab_service import get_active_deployment

router = APIRouter(prefix="/labs", tags=["labs"])


def _enrich(template: LabTemplate, db: Session) -> LabTemplateResponse:
    active = get_active_deployment(db, template.id)
    current = DeploymentSummary.model_validate(active) if active else None
    data = LabTemplateResponse.model_validate(template)
    data.current_deployment = current
    return data


@router.get("/", response_model=list[LabTemplateResponse])
def list_labs(
    category: Optional[str] = Query(None, description="world | firerange | thirdparty"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[LabTemplateResponse]:
    q = db.query(LabTemplate).filter(LabTemplate.is_active == True)  # noqa: E712
    if category:
        q = q.filter(LabTemplate.category == category)
    templates = q.order_by(LabTemplate.id).all()
    return [_enrich(t, db) for t in templates]


@router.get("/{lab_id}", response_model=LabTemplateResponse)
def get_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> LabTemplateResponse:
    template = db.get(LabTemplate, lab_id)
    if template is None:
        raise not_found("Lab")
    return _enrich(template, db)
