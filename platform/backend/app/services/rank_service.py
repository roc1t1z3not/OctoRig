# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Optional

from sqlalchemy.orm import Session

from app.models.rank import Rank

RANK_SEED = [
    {"name": "Recruit",      "min_points": 0,         "icon": "user",      "color": "#6b7280"},
    {"name": "Trainee",      "min_points": 100,        "icon": "shield",    "color": "#64748b"},
    {"name": "Novice",       "min_points": 500,        "icon": "target",    "color": "#22c55e"},
    {"name": "Apprentice",   "min_points": 1_000,      "icon": "key",       "color": "#16a34a"},
    {"name": "Explorer",     "min_points": 2_500,      "icon": "compass",   "color": "#3b82f6"},
    {"name": "Initiate",     "min_points": 5_000,      "icon": "unlock",    "color": "#2563eb"},
    {"name": "Hacker",       "min_points": 10_000,     "icon": "terminal",  "color": "#a855f7"},
    {"name": "Specialist",   "min_points": 20_000,     "icon": "code-2",    "color": "#9333ea"},
    {"name": "Operator",     "min_points": 35_000,     "icon": "zap",       "color": "#f59e0b"},
    {"name": "Expert",       "min_points": 50_000,     "icon": "cpu",       "color": "#d97706"},
    {"name": "Infiltrator",  "min_points": 75_000,     "icon": "eye",       "color": "#ef4444"},
    {"name": "Phantom",      "min_points": 100_000,    "icon": "ghost",     "color": "#dc2626"},
    {"name": "Shadow",       "min_points": 150_000,    "icon": "moon",      "color": "#ec4899"},
    {"name": "Ghost",        "min_points": 250_000,    "icon": "radar",     "color": "#db2777"},
    {"name": "Veteran",      "min_points": 400_000,    "icon": "skull",     "color": "#f97316"},
    {"name": "Elite",        "min_points": 600_000,    "icon": "flame",     "color": "#ea580c"},
    {"name": "Master",       "min_points": 900_000,    "icon": "crown",     "color": "#eab308"},
    {"name": "Legend",       "min_points": 1_500_000,  "icon": "award",     "color": "#ca8a04"},
    {"name": "Grandmaster",  "min_points": 2_500_000,  "icon": "trophy",    "color": "#06b6d4"},
    {"name": "Apex",         "min_points": 5_000_000,  "icon": "octagon",   "color": "#0891b2"},
]


def get_rank_for_points(db: Session, points: int) -> Optional[Rank]:
    return (
        db.query(Rank)
        .filter(Rank.is_active.is_(True), Rank.min_points <= points)
        .order_by(Rank.min_points.desc())
        .first()
    )


def get_next_rank(db: Session, points: int) -> Optional[Rank]:
    return (
        db.query(Rank)
        .filter(Rank.is_active.is_(True), Rank.min_points > points)
        .order_by(Rank.min_points.asc())
        .first()
    )


def seed_ranks(db: Session) -> int:
    if db.query(Rank).count() > 0:
        return 0
    inserted = 0
    for entry in RANK_SEED:
        db.add(Rank(**entry))
        inserted += 1
    db.commit()
    return inserted
