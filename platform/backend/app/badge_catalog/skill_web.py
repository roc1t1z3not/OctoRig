from app.models.badge import AchievementRuleType

WEB_BADGES = [
    {
        "slug": "web-first",
        "name": "Web Rookie",
        "description": "Solved your first web exploitation challenge.",
        "icon": "globe",
        "category": "skill",
        "points_value": 10,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "web"},
    },
    {
        "slug": "web-five",
        "name": "Exploit Curious",
        "description": "Solved 5 web exploitation challenges.",
        "icon": "network",
        "category": "skill",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "web"},
    },
    {
        "slug": "web-ten",
        "name": "Exploit Dev",
        "description": "Solved 10 web exploitation challenges.",
        "icon": "bug",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 10, "category": "web"},
    },
    {
        "slug": "web-master",
        "name": "Web Wizard",
        "description": "Completed every web exploitation challenge.",
        "icon": "wand-sparkles",
        "category": "skill",
        "points_value": 500,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "web"},
    },
]
