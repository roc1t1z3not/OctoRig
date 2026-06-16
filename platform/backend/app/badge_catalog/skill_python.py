# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from app.models.badge import AchievementRuleType

PYTHON_BADGES = [
    {
        "slug": "python-first",
        "name": "Serpent's Touch",
        "description": "Wrote your first exploit in Python.",
        "icon": "terminal",
        "category": "skill",
        "points_value": 10,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "python"},
    },
    {
        "slug": "python-three",
        "name": "Pythonista",
        "description": "Python is your weapon of choice.",
        "icon": "braces",
        "category": "skill",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "python"},
    },
    {
        "slug": "python-five",
        "name": "Script Surgeon",
        "description": "Automating the pain away.",
        "icon": "code-2",
        "category": "skill",
        "points_value": 100,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "python"},
    },
    {
        "slug": "python-master",
        "name": "Ouroboros",
        "description": "Solved all Python challenges.",
        "icon": "infinity",
        "category": "skill",
        "points_value": 400,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "python"},
    },
]
