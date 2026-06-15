from app.models.badge import AchievementRuleType

XSS_BADGES = [
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
        "icon": "triangle-alert",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "xss"},
    },
    {
        "slug": "xss-five",
        "name": "DOM Defacer",
        "description": "Solved 5 XSS challenges.",
        "icon": "square-code",
        "category": "skill",
        "points_value": 75,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "xss"},
    },
    {
        "slug": "xss-master",
        "name": "Web Exploiter",
        "description": "Solved all XSS challenges.",
        "icon": "sparkles",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "xss"},
    },
]
