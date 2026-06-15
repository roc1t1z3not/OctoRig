from app.models.badge import AchievementRuleType

SQLI_BADGES = [
    {
        "slug": "sqli-first",
        "name": "Injector",
        "description": "Solved your first SQL injection challenge.",
        "icon": "database",
        "category": "skill",
        "points_value": 10,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 1, "category": "sqli"},
    },
    {
        "slug": "sqli-five",
        "name": "Query Bender",
        "description": "Solved 5 SQL injection challenges.",
        "icon": "table-2",
        "category": "skill",
        "points_value": 50,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 5, "category": "sqli"},
    },
    {
        "slug": "sqli-ten",
        "name": "SQL Ninja",
        "description": "Solved 10 SQL injection challenges.",
        "icon": "server",
        "category": "skill",
        "points_value": 150,
        "rule_type": AchievementRuleType.SOLVE_COUNT,
        "rule_config": {"threshold": 10, "category": "sqli"},
    },
    {
        "slug": "sql-master",
        "name": "SQL Slinger",
        "description": "Solved all SQL Injection challenges.",
        "icon": "database-zap",
        "category": "skill",
        "points_value": 300,
        "rule_type": AchievementRuleType.CATEGORY_COMPLETE,
        "rule_config": {"category": "sqli"},
    },
]
