from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg2://octorig:octorig@localhost:5432/octorig"

    # Security
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Admin seeding (used on first startup if no users exist)
    admin_username: str = "admin"
    admin_email: str = "admin@octorig.local"
    admin_password: str = "changeme"

    # Docker / Labs
    labs_root: str = "/octorig/labs"

    # CORS — comma-separated string; split into list by the app at startup
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    def get_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"


settings = Settings()
