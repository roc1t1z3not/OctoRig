from datetime import datetime, timezone
from typing import Any, Optional

import redis as redis_lib
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.config import settings
from app.core.exceptions import bad_request, not_found
from app.models.challenge import ChallengeDifficulty, ChallengeType
from app.models.user import User
from app.services import audit_service
from app.services.challenge_service import (
    get_challenge_by_slug_or_404, get_solve_count,
    get_unlocked_hint_ids, list_challenges, submit_flag, unlock_hint,
)
from app.services.scoring_service import ScoreTransactionSource, award_points, get_user_score

router = APIRouter(prefix="/challenges", tags=["challenges"])

_redis: Optional[redis_lib.Redis] = None


def _get_redis() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
    return _redis


# ── Rate limiting ─────────────────────────────────────────────────────────────

_RATE_LIMIT = 10
_RATE_WINDOW = 60  # seconds


def _check_submit_rate_limit(user_id: int, challenge_id: int) -> None:
    key = f"flag:ratelimit:{user_id}:{challenge_id}"
    r = _get_redis()
    count = r.incr(key)
    if count == 1:
        r.expire(key, _RATE_WINDOW)
    if count > _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many attempts. Try again in {r.ttl(key)} seconds.",
        )


# ── Schemas ───────────────────────────────────────────────────────────────────

class HintResponse(BaseModel):
    id: int
    order_num: int
    cost: int
    content: Optional[str] = None
    unlocked: bool = False

    model_config = {"from_attributes": True}


class ChallengeListItem(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: ChallengeDifficulty
    category: str
    tags: list[str]
    points: int
    challenge_type: ChallengeType
    estimated_minutes: Optional[int]
    solve_count: int = 0
    solved_by_me: bool = False

    model_config = {"from_attributes": True}


class ChallengeDetail(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: ChallengeDifficulty
    category: str
    tags: list[Any]
    skills: list[Any]
    points: int
    challenge_type: ChallengeType
    estimated_minutes: Optional[int]
    content: dict[str, Any]
    hints: list[HintResponse]
    files: list[dict[str, Any]]
    solve_count: int = 0
    solved_by_me: bool = False
    version: int

    model_config = {"from_attributes": True}


class FlagSubmitRequest(BaseModel):
    flag: str = Field(..., min_length=1, max_length=512)
    event_id: Optional[int] = None


class FlagSubmitResponse(BaseModel):
    correct: bool
    already_solved: bool
    first_blood: bool
    points_awarded: int
    message: str


class HintUnlockResponse(BaseModel):
    hint_id: int
    content: str
    cost: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize_hint(hint, unlocked_ids: set[int]) -> HintResponse:
    unlocked = hint.id in unlocked_ids
    return HintResponse(
        id=hint.id,
        order_num=hint.order_num,
        cost=hint.cost,
        content=hint.content if unlocked else None,
        unlocked=unlocked,
    )


def _get_team_id(db: Session, user: User) -> Optional[int]:
    from app.models.team import TeamMember
    membership = (
        db.query(TeamMember)
        .filter(TeamMember.user_id == user.id)
        .first()
    )
    return membership.team_id if membership else None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ChallengeListItem])
def list_challenges_endpoint(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChallengeListItem]:
    from app.services.challenge_service import check_already_solved
    challenges = list_challenges(db, category=category, difficulty=difficulty, search=search, tag=tag)
    items = []
    for ch in challenges:
        items.append(
            ChallengeListItem(
                id=ch.id,
                slug=ch.slug,
                title=ch.title,
                difficulty=ch.difficulty,
                category=ch.category,
                tags=ch.tags,
                points=ch.points,
                challenge_type=ch.challenge_type,
                estimated_minutes=ch.estimated_minutes,
                solve_count=get_solve_count(db, ch.id),
                solved_by_me=check_already_solved(db, ch.id, current_user.id),
            )
        )
    return items


@router.get("/{slug}", response_model=ChallengeDetail)
def get_challenge_endpoint(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChallengeDetail:
    from app.services.challenge_service import check_already_solved
    ch = get_challenge_by_slug_or_404(db, slug)
    unlocked_ids = get_unlocked_hint_ids(db, current_user.id, ch.id)
    return ChallengeDetail(
        id=ch.id,
        slug=ch.slug,
        title=ch.title,
        description=ch.description,
        difficulty=ch.difficulty,
        category=ch.category,
        tags=ch.tags,
        skills=ch.skills,
        points=ch.points,
        challenge_type=ch.challenge_type,
        estimated_minutes=ch.estimated_minutes,
        content=ch.content,
        hints=[_serialize_hint(h, unlocked_ids) for h in ch.hints],
        files=[{"id": f.id, "filename": f.filename, "size_bytes": f.size_bytes} for f in ch.files],
        solve_count=get_solve_count(db, ch.id),
        solved_by_me=check_already_solved(db, ch.id, current_user.id),
        version=ch.version,
    )


@router.post("/{slug}/submit", response_model=FlagSubmitResponse)
def submit_flag_endpoint(
    slug: str,
    body: FlagSubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FlagSubmitResponse:
    ch = get_challenge_by_slug_or_404(db, slug)
    _check_submit_rate_limit(current_user.id, ch.id)

    ip = request.client.host if request.client else None
    team_id = _get_team_id(db, current_user)

    result = submit_flag(
        db,
        challenge_id=ch.id,
        submitted_value=body.flag,
        user_id=current_user.id,
        team_id=team_id,
        event_id=body.event_id,
        ip_address=ip,
    )

    if result.already_solved:
        return FlagSubmitResponse(
            correct=True, already_solved=True, first_blood=False,
            points_awarded=0, message="Already solved.",
        )

    audit_service.write_audit(
        db,
        action=audit_service.CHALLENGE_SUBMITTED,
        user_id=current_user.id,
        detail={"challenge_id": ch.id, "slug": ch.slug, "correct": result.correct},
        ip=ip,
    )

    if result.correct:
        award_points(
            db,
            user_id=current_user.id,
            points=result.points_awarded,
            source_type=ScoreTransactionSource.CHALLENGE_SOLVE,
            source_id=ch.id,
            team_id=team_id,
            event_id=body.event_id,
        )
        audit_service.write_audit(
            db,
            action=audit_service.CHALLENGE_SOLVED,
            user_id=current_user.id,
            detail={
                "challenge_id": ch.id,
                "slug": ch.slug,
                "first_blood": result.first_blood,
                "points": result.points_awarded,
            },
            ip=ip,
        )
        msg = "First blood! " if result.first_blood else ""
        msg += f"Correct! +{result.points_awarded} points."
        return FlagSubmitResponse(
            correct=True, already_solved=False,
            first_blood=result.first_blood,
            points_awarded=result.points_awarded,
            message=msg,
        )

    return FlagSubmitResponse(
        correct=False, already_solved=False, first_blood=False,
        points_awarded=0, message="Incorrect flag.",
    )


@router.post("/{slug}/hints/{hint_id}/unlock", response_model=HintUnlockResponse)
def unlock_hint_endpoint(
    slug: str,
    hint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintUnlockResponse:
    ch = get_challenge_by_slug_or_404(db, slug)
    hint = unlock_hint(db, hint_id, current_user.id)

    if hint.challenge_id != ch.id:
        raise not_found("Hint")

    if hint.cost > 0:
        balance = get_user_score(db, current_user.id)
        if balance < hint.cost:
            raise bad_request(f"Not enough points — hint costs {hint.cost} but you have {balance}.")
        team_id = _get_team_id(db, current_user)
        from app.services.scoring_service import deduct_hint_cost
        deduct_hint_cost(db, user_id=current_user.id, cost=hint.cost, hint_id=hint_id, team_id=team_id)

    return HintUnlockResponse(hint_id=hint.id, content=hint.content, cost=hint.cost)
