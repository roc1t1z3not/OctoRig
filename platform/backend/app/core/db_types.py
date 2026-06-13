from sqlalchemy import Enum as _SAEnum


def EnumCol(enum_class, **kwargs):
    """SQLAlchemy Enum column that stores .value (not .name) for native Postgres enums."""
    return _SAEnum(
        enum_class,
        values_callable=lambda obj: [e.value for e in obj],
        **kwargs,
    )
