from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import bad_request, forbidden_exception, not_found
from app.models.content import (
    ContentReview, ContentStatus, ContentSubmission, ContentType, ReviewVerdict,
)
from app.models.user import User
from app.services import audit_service


# ── Platform role guard ───────────────────────────────────────────────────────

def require_platform_role(role: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        roles: list[str] = current_user.platform_roles or []
        if role not in roles and not current_user.is_admin and not current_user.is_superuser:
            raise forbidden_exception
        return current_user
    return dependency


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_submission(
    db: Session,
    author_id: int,
    content_type: ContentType,
    title: str,
    body: dict[str, Any],
) -> ContentSubmission:
    sub = ContentSubmission(
        author_id=author_id,
        content_type=content_type,
        title=title,
        body=body,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    audit_service.write_audit(db, audit_service.CONTENT_SUBMITTED, user_id=author_id, detail={"id": sub.id, "title": title})
    return sub


def get_submission_or_404(db: Session, submission_id: int) -> ContentSubmission:
    sub = db.get(ContentSubmission, submission_id)
    if sub is None:
        raise not_found("Submission")
    return sub


def list_submissions(
    db: Session,
    author_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[ContentSubmission]:
    q = db.query(ContentSubmission)
    if author_id is not None:
        q = q.filter(ContentSubmission.author_id == author_id)
    if status is not None:
        q = q.filter(ContentSubmission.status == ContentStatus(status))
    return q.order_by(ContentSubmission.created_at.desc()).all()


def update_submission(
    db: Session,
    submission: ContentSubmission,
    title: Optional[str],
    body: Optional[dict[str, Any]],
) -> ContentSubmission:
    if submission.status not in (ContentStatus.DRAFT, ContentStatus.REJECTED):
        raise bad_request("Can only edit drafts or rejected submissions")
    if title is not None:
        submission.title = title
    if body is not None:
        submission.body = body
    submission.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(submission)
    return submission


def submit_for_review(db: Session, submission: ContentSubmission) -> ContentSubmission:
    if submission.status != ContentStatus.DRAFT:
        raise bad_request("Only drafts can be submitted for review")
    submission.status = ContentStatus.PENDING_REVIEW
    submission.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(submission)
    return submission


# ── Review workflow ───────────────────────────────────────────────────────────

def claim_review(db: Session, submission: ContentSubmission, reviewer_id: int) -> ContentSubmission:
    if submission.status != ContentStatus.PENDING_REVIEW:
        raise bad_request("Submission is not pending review")
    submission.status = ContentStatus.IN_REVIEW
    submission.reviewer_id = reviewer_id
    submission.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(submission)
    return submission


def record_review(
    db: Session,
    submission: ContentSubmission,
    reviewer_id: int,
    verdict: ReviewVerdict,
    comment: Optional[str],
) -> ContentReview:
    if submission.status not in (ContentStatus.IN_REVIEW,):
        raise bad_request("Submission is not in review")

    review = ContentReview(
        submission_id=submission.id,
        reviewer_id=reviewer_id,
        verdict=verdict,
        comment=comment,
    )
    db.add(review)

    if verdict == ReviewVerdict.APPROVED:
        submission.status = ContentStatus.APPROVED
    elif verdict == ReviewVerdict.REJECTED:
        submission.status = ContentStatus.REJECTED
        audit_service.write_audit(db, audit_service.CONTENT_REJECTED, user_id=reviewer_id, detail={"id": submission.id})
    elif verdict == ReviewVerdict.NEEDS_CHANGES:
        submission.status = ContentStatus.DRAFT

    submission.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(review)
    return review


def publish_submission(db: Session, submission: ContentSubmission, publisher_id: int) -> ContentSubmission:
    if submission.status != ContentStatus.APPROVED:
        raise bad_request("Only approved submissions can be published")
    submission.status = ContentStatus.PUBLISHED
    submission.updated_at = datetime.now(timezone.utc)
    db.commit()
    audit_service.write_audit(db, audit_service.CONTENT_PUBLISHED, user_id=publisher_id, detail={"id": submission.id})
    db.refresh(submission)
    return submission
