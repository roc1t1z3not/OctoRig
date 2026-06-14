from typing import Any, Callable, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.badge import AchievementRule, AchievementRuleType, BadgeDefinition, UserBadge
from app.models.challenge import ChallengeSubmission
from app.models.scoring import ScoreTransaction
from app.services import audit_service
from app.services.scoring_service import ScoreTransactionSource, award_points


# ── Rule evaluators ───────────────────────────────────────────────────────────
# Each evaluator returns True if the rule is satisfied for the given user.

def _eval_solve_count(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    from app.models.challenge import Challenge
    threshold = config.get("threshold", 1)
    category = config.get("category")
    q = (
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
        )
    )
    if category:
        q = (
            q.join(Challenge, ChallengeSubmission.challenge_id == Challenge.id)
            .filter(Challenge.category == category)
        )
    return (q.scalar() or 0) >= threshold


def _eval_first_blood(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    threshold = config.get("threshold", 1)
    count = (
        db.query(func.count(ChallengeSubmission.id))
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
            ChallengeSubmission.is_first_blood.is_(True),
        )
        .scalar() or 0
    )
    return count >= threshold


def _eval_category_complete(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    from app.models.challenge import Challenge
    category = config.get("category")
    if not category:
        return False
    total = (
        db.query(func.count(Challenge.id))
        .filter(Challenge.category == category, Challenge.is_active.is_(True), Challenge.is_archived.is_(False))
        .scalar() or 0
    )
    if total == 0:
        return False
    solved = (
        db.query(func.count(ChallengeSubmission.id))
        .join(Challenge, ChallengeSubmission.challenge_id == Challenge.id)
        .filter(
            ChallengeSubmission.user_id == user_id,
            ChallengeSubmission.is_correct.is_(True),
            Challenge.category == category,
        )
        .scalar() or 0
    )
    return solved >= total


def _eval_points_threshold(db: Session, user_id: int, config: dict[str, Any]) -> bool:
    threshold = config.get("threshold", 0)
    total = (
        db.query(func.coalesce(func.sum(ScoreTransaction.points), 0))
        .filter(ScoreTransaction.user_id == user_id)
        .scalar() or 0
    )
    return int(total) >= threshold


def _eval_manual(_db: Session, _user_id: int, _config: dict[str, Any]) -> bool:
    return False  # manual badges are never auto-awarded


_EVALUATORS: dict[AchievementRuleType, Callable] = {
    AchievementRuleType.SOLVE_COUNT:       _eval_solve_count,
    AchievementRuleType.FIRST_BLOOD:       _eval_first_blood,
    AchievementRuleType.STREAK_DAYS:       lambda *_: False,  # not yet implemented
    AchievementRuleType.CATEGORY_COMPLETE: _eval_category_complete,
    AchievementRuleType.POINTS_THRESHOLD:  _eval_points_threshold,
    AchievementRuleType.MANUAL:            _eval_manual,
}


# ── Badge award ───────────────────────────────────────────────────────────────

def _already_earned(db: Session, user_id: int, badge_id: int) -> bool:
    return (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        .first()
    ) is not None


def award_badge(
    db: Session,
    user_id: int,
    badge: BadgeDefinition,
    awarded_by_id: Optional[int] = None,
    note: Optional[str] = None,
) -> Optional[UserBadge]:
    if _already_earned(db, user_id, badge.id):
        return None

    ub = UserBadge(
        user_id=user_id,
        badge_id=badge.id,
        awarded_by_id=awarded_by_id,
        note=note,
    )
    db.add(ub)
    db.flush()

    if badge.points_value > 0:
        award_points(
            db,
            user_id=user_id,
            points=badge.points_value,
            source_type=ScoreTransactionSource.BADGE_AWARD,
            source_id=badge.id,
        )

    audit_service.write_audit(
        db,
        action=audit_service.BADGE_AWARDED,
        user_id=user_id,
        detail={"badge_slug": badge.slug, "badge_name": badge.name},
    )
    db.commit()
    return ub


# ── Evaluation entry point ────────────────────────────────────────────────────

def evaluate_achievements(db: Session, user_id: int) -> list[str]:
    """Check all active rules for user_id; award any newly-earned badges.

    Returns slugs of newly awarded badges.
    """
    rules: list[AchievementRule] = (
        db.query(AchievementRule)
        .join(BadgeDefinition, AchievementRule.badge_id == BadgeDefinition.id)
        .filter(AchievementRule.is_active.is_(True), BadgeDefinition.is_active.is_(True))
        .all()
    )

    awarded: list[str] = []
    evaluated_badges: set[int] = set()

    for rule in rules:
        badge = rule.badge
        if badge.id in evaluated_badges:
            continue
        if _already_earned(db, user_id, badge.id):
            evaluated_badges.add(badge.id)
            continue

        evaluator = _EVALUATORS.get(rule.rule_type)
        if evaluator is None:
            continue

        try:
            met = evaluator(db, user_id, rule.rule_config)
        except Exception:
            continue

        if met:
            result = award_badge(db, user_id, badge)
            if result:
                awarded.append(badge.slug)
            evaluated_badges.add(badge.id)

    return awarded


# ── Badge catalog seeding ─────────────────────────────────────────────────────

SEED_CATALOG = [
    {
        "slug": "first-steps",
        "name": "First Steps",
        "description": "Solved your first challenge.",
        "icon": "flag",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1},
    },
    {
        "slug": "ten-solves",
        "name": "Ten Solver",
        "description": "Solved 10 challenges.",
        "icon": "hash",
        "category": "milestone",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 10},
    },
    {
        "slug": "fifty-solves",
        "name": "Grinder",
        "description": "Solved 50 challenges.",
        "icon": "zap",
        "category": "milestone",
        "points_value": 200,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 50},
    },
    {
        "slug": "first-blood",
        "name": "Bloodhound",
        "description": "Achieved first blood on any challenge.",
        "icon": "droplets",
        "category": "competition",
        "points_value": 100,
        "rule_type": AchievementRuleType.FIRST_BLOOD,
        "rule_config": {},
    },
    {
        "slug": "sql-master",
        "name": "SQL Slinger",
        "description": "Solved all SQL Injection challenges.",
        "icon": "database",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "sql-injection"},
    },
    {
        "slug": "xss-master",
        "name": "Web Exploiter",
        "description": "Solved all XSS challenges.",
        "icon": "code",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "xss"},
    },
    {
        "slug": "idor-master",
        "name": "Access Denied",
        "description": "Solved all IDOR challenges.",
        "icon": "lock",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "idor"},
    },
    {
        "slug": "points-1k",
        "name": "Point Collector",
        "description": "Reached 1,000 total points.",
        "icon": "star",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 1000},
    },
    {
        "slug": "points-10k",
        "name": "Elite",
        "description": "Reached 10,000 total points.",
        "icon": "crown",
        "category": "milestone",
        "points_value": 500,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 10000},
    },
    # ── Milestone (extended) ──────────────────────────────────────────────────
    {
        "slug": "twenty-five-solves",
        "name": "On a Roll",
        "description": "Solved 25 challenges.",
        "icon": "target",
        "category": "milestone",
        "points_value": 75,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 25},
    },
    {
        "slug": "hundred-solves",
        "name": "Centurion",
        "description": "Solved 100 challenges.",
        "icon": "trophy",
        "category": "milestone",
        "points_value": 1000,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 100},
    },
    {
        "slug": "points-5k",
        "name": "High Scorer",
        "description": "Reached 5,000 total points.",
        "icon": "star",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 5000},
    },
    {
        "slug": "points-25k",
        "name": "Legend",
        "description": "Reached 25,000 total points.",
        "icon": "flame",
        "category": "milestone",
        "points_value": 1000,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 25000},
    },
    # ── Competition (extended) ────────────────────────────────────────────────
    {
        "slug": "triple-blood",
        "name": "Serial Bleeder",
        "description": "Achieved first blood on 3 different challenges.",
        "icon": "droplets",
        "category": "competition",
        "points_value": 200,
        "rule_type": AchievementRuleType.FIRST_BLOOD,
        "rule_config": {"threshold": 3},
    },
    {
        "slug": "ten-bloods",
        "name": "Bloodbath",
        "description": "Achieved first blood on 10 different challenges.",
        "icon": "skull",
        "category": "competition",
        "points_value": 500,
        "rule_type": AchievementRuleType.FIRST_BLOOD,
        "rule_config": {"threshold": 10},
    },
    # ── Skill (extended) ─────────────────────────────────────────────────────
    {
        "slug": "recon-master",
        "name": "Reconnoisseur",
        "description": "Completed every recon challenge.",
        "icon": "eye",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "recon"},
    },
    {
        "slug": "web-master",
        "name": "Web Wizard",
        "description": "Completed every web exploitation challenge.",
        "icon": "globe",
        "category": "skill",
        "points_value": 500,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "web"},
    },
    # ── XSS progression (9 total) ─────────────────────────────────────────────
    {
        "slug": "xss-first",
        "name": "Script Kiddie",
        "description": "Solved your first XSS challenge.",
        "icon": "code",
        "category": "skill",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "xss"},
    },
    {
        "slug": "xss-three",
        "name": "Alert!",
        "description": "Solved 3 XSS challenges.",
        "icon": "code",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "xss"},
    },
    {
        "slug": "xss-five",
        "name": "DOM Defacer",
        "description": "Solved 5 XSS challenges.",
        "icon": "code",
        "category": "skill",
        "points_value": 75,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "xss"},
    },
    # ── SQLi progression (20 total) ───────────────────────────────────────────
    {
        "slug": "sqli-first",
        "name": "Injector",
        "description": "Solved your first SQL injection challenge.",
        "icon": "database",
        "category": "skill",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "sqli"},
    },
    {
        "slug": "sqli-five",
        "name": "Query Bender",
        "description": "Solved 5 SQL injection challenges.",
        "icon": "database",
        "category": "skill",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "sqli"},
    },
    {
        "slug": "sqli-ten",
        "name": "SQL Ninja",
        "description": "Solved 10 SQL injection challenges.",
        "icon": "database",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 10, "category": "sqli"},
    },
    # ── IDOR progression (13 total) ───────────────────────────────────────────
    {
        "slug": "idor-first",
        "name": "Snooper",
        "description": "Solved your first IDOR challenge.",
        "icon": "lock",
        "category": "skill",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "idor"},
    },
    {
        "slug": "idor-three",
        "name": "Boundary Pusher",
        "description": "Solved 3 IDOR challenges.",
        "icon": "lock",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "idor"},
    },
    {
        "slug": "idor-seven",
        "name": "Access Broker",
        "description": "Solved 7 IDOR challenges.",
        "icon": "lock",
        "category": "skill",
        "points_value": 100,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 7, "category": "idor"},
    },
    # ── Recon progression (8 total) ───────────────────────────────────────────
    {
        "slug": "recon-first",
        "name": "Lurker",
        "description": "Completed your first recon challenge.",
        "icon": "eye",
        "category": "skill",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "recon"},
    },
    {
        "slug": "recon-three",
        "name": "Intel Gatherer",
        "description": "Completed 3 recon challenges.",
        "icon": "eye",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "recon"},
    },
    {
        "slug": "recon-five",
        "name": "Surface Mapper",
        "description": "Completed 5 recon challenges.",
        "icon": "eye",
        "category": "skill",
        "points_value": 75,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "recon"},
    },
    # ── Web progression (22 total) ────────────────────────────────────────────
    {
        "slug": "web-first",
        "name": "Web Rookie",
        "description": "Solved your first web exploitation challenge.",
        "icon": "globe",
        "category": "skill",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "web"},
    },
    {
        "slug": "web-five",
        "name": "Exploit Curious",
        "description": "Solved 5 web exploitation challenges.",
        "icon": "globe",
        "category": "skill",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "web"},
    },
    {
        "slug": "web-ten",
        "name": "Exploit Dev",
        "description": "Solved 10 web exploitation challenges.",
        "icon": "globe",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 10, "category": "web"},
    },
    # ── Milestone (extended) ──────────────────────────────────────────────────
    {
        "slug": "five-solves",
        "name": "Getting Started",
        "description": "Solved 5 challenges.",
        "icon": "flag",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5},
    },
    {
        "slug": "points-500",
        "name": "First Score",
        "description": "Reached 500 total points.",
        "icon": "zap",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 500},
    },
    {
        "slug": "points-2500",
        "name": "Gaining Ground",
        "description": "Reached 2,500 total points.",
        "icon": "star",
        "category": "milestone",
        "points_value": 0,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 2500},
    },
    {
        "slug": "points-50k",
        "name": "Unstoppable",
        "description": "Reached 50,000 total points.",
        "icon": "flame",
        "category": "milestone",
        "points_value": 2000,
        "rule_type": AchievementRuleType.POINTS_THRESHOLD,
        "rule_config": {"threshold": 50000},
    },
    # ── Competition (extended) ────────────────────────────────────────────────
    {
        "slug": "five-bloods",
        "name": "Knife's Edge",
        "description": "Achieved first blood on 5 different challenges.",
        "icon": "skull",
        "category": "competition",
        "points_value": 300,
        "rule_type": AchievementRuleType.FIRST_BLOOD,
        "rule_config": {"threshold": 5},
    },
]


# rule_config corrections for already-seeded badges
_RULE_CONFIG_FIXUPS: dict[str, dict] = {
    "sql-master": {"category": "sqli"},  # was "sql-injection", challenges use "sqli"
}


def seed_badge_catalog(db: Session) -> int:
    """Insert built-in badges if they don't already exist. Returns count inserted."""
    # Patch any stale rule configs before seeding new ones
    for slug, correct_config in _RULE_CONFIG_FIXUPS.items():
        badge = db.query(BadgeDefinition).filter(BadgeDefinition.slug == slug).first()
        if badge and badge.rules and badge.rules[0].rule_config != correct_config:
            badge.rules[0].rule_config = correct_config
            db.commit()

    inserted = 0
    for entry in SEED_CATALOG:
        existing = db.query(BadgeDefinition).filter(BadgeDefinition.slug == entry["slug"]).first()
        if existing:
            continue
        badge = BadgeDefinition(
            slug=entry["slug"],
            name=entry["name"],
            description=entry["description"],
            icon=entry["icon"],
            category=entry["category"],
            points_value=entry["points_value"],
        )
        db.add(badge)
        db.flush()
        rule = AchievementRule(
            badge_id=badge.id,
            rule_type=entry["rule_type"],
            rule_config=entry["rule_config"],
        )
        db.add(rule)
        db.commit()
        inserted += 1
    return inserted
