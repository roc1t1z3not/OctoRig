from app.models.badge import AchievementRuleType

RECON_BADGES = [
    {
        "slug": "recon-first",
        "name": "Lurker",
        "description": "Completed your first recon challenge.",
        "icon": "eye",
        "category": "skill",
        "points_value": 10,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "recon"},
    },
    {
        "slug": "recon-three",
        "name": "Intel Gatherer",
        "description": "Completed 3 recon challenges.",
        "icon": "binoculars",
        "category": "skill",
        "points_value": 25,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 3, "category": "recon"},
    },
    {
        "slug": "recon-five",
        "name": "Surface Mapper",
        "description": "Completed 5 recon challenges.",
        "icon": "map",
        "category": "skill",
        "points_value": 75,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "recon"},
    },
    {
        "slug": "recon-master",
        "name": "Reconnoisseur",
        "description": "Completed every recon challenge.",
        "icon": "radar",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "recon"},
    },
]
