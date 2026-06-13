from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models.content import ContentStatus, ContentType, ReviewVerdict
from app.models.user import User
from app.services.content_service import (
    claim_review, create_submission, get_submission_or_404,
    list_submissions, publish_submission, record_review,
    require_platform_role, submit_for_review, update_submission,
)

router = APIRouter(prefix="/content", tags=["content"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SubmissionOut(BaseModel):
    id: int
    author_id: int
    content_type: ContentType
    title: str
    body: dict[str, Any]
    status: ContentStatus
    reviewer_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateRequest(BaseModel):
    content_type: ContentType
    title: str
    body: dict[str, Any] = {}


class UpdateRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[dict[str, Any]] = None


class ReviewRequest(BaseModel):
    verdict: ReviewVerdict
    comment: Optional[str] = None


# ── Creator endpoints ─────────────────────────────────────────────────────────

@router.post("/", response_model=SubmissionOut)
def create_endpoint(
    body: CreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_role("creator")),
) -> SubmissionOut:
    return create_submission(db, current_user.id, body.content_type, body.title, body.body)


@router.get("/mine", response_model=list[SubmissionOut])
def list_mine(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SubmissionOut]:
    return list_submissions(db, author_id=current_user.id, status=status)


@router.get("/{submission_id}", response_model=SubmissionOut)
def get_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionOut:
    sub = get_submission_or_404(db, submission_id)
    if sub.author_id != current_user.id and not current_user.is_admin:
        roles: list[str] = current_user.platform_roles or []
        if "reviewer" not in roles and "publisher" not in roles:
            from app.core.exceptions import forbidden_exception
            raise forbidden_exception
    return sub


@router.patch("/{submission_id}", response_model=SubmissionOut)
def update_endpoint(
    submission_id: int,
    body: UpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionOut:
    sub = get_submission_or_404(db, submission_id)
    if sub.author_id != current_user.id:
        from app.core.exceptions import forbidden_exception
        raise forbidden_exception
    return update_submission(db, sub, body.title, body.body)


@router.post("/{submission_id}/submit", response_model=SubmissionOut)
def submit_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionOut:
    sub = get_submission_or_404(db, submission_id)
    if sub.author_id != current_user.id:
        from app.core.exceptions import forbidden_exception
        raise forbidden_exception
    return submit_for_review(db, sub)


# ── Reviewer endpoints ────────────────────────────────────────────────────────

@router.get("/queue/pending", response_model=list[SubmissionOut])
def pending_queue(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_role("reviewer")),
) -> list[SubmissionOut]:
    return list_submissions(db, status="pending_review")


@router.post("/{submission_id}/claim", response_model=SubmissionOut)
def claim_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_role("reviewer")),
) -> SubmissionOut:
    sub = get_submission_or_404(db, submission_id)
    return claim_review(db, sub, current_user.id)


@router.post("/{submission_id}/review", response_model=dict[str, Any])
def review_endpoint(
    submission_id: int,
    body: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_role("reviewer")),
) -> dict[str, Any]:
    sub = get_submission_or_404(db, submission_id)
    review = record_review(db, sub, current_user.id, body.verdict, body.comment)
    return {
        "review_id": review.id,
        "verdict": review.verdict.value,
        "submission_status": sub.status.value,
    }


# ── Publisher endpoints ───────────────────────────────────────────────────────

@router.get("/queue/approved", response_model=list[SubmissionOut])
def approved_queue(
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_role("publisher")),
) -> list[SubmissionOut]:
    return list_submissions(db, status="approved")


@router.post("/{submission_id}/publish", response_model=SubmissionOut)
def publish_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_platform_role("publisher")),
) -> SubmissionOut:
    sub = get_submission_or_404(db, submission_id)
    return publish_submission(db, sub, current_user.id)
