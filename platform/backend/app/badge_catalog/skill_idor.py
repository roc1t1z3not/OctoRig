# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from app.models.badge import AchievementRuleType

IDOR_BADGES = [
    {
        "slug": "idor-first",
        "name": "Snooper",
        "description": "Solved your first IDOR challenge.",
        "icon": "lock",
        "category": "skill",
        "points_value": 10,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "idor"},
    },
    {
        "slug": "idor-three",
        "name": "Boundary Pusher",
        "description": "Solved 3 IDOR challenges.",
        "icon": "lock-open",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "idor"},
    },
    {
        "slug": "idor-seven",
        "name": "Access Broker",
        "description": "Solved 7 IDOR challenges.",
        "icon": "key-round",
        "category": "skill",
        "points_value": 100,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 7, "category": "idor"},
    },
    {
        "slug": "idor-master",
        "name": "Access Denied",
        "description": "Solved all IDOR challenges.",
        "icon": "shield-off",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "idor"},
    },
]
