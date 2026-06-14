from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRETS = {
    "change-me-in-production-use-a-long-random-string",
    "change-me-in-production",
    "secret",
    "changeme",
}
_INSECURE_PASSWORDS = {"changeme", "admin", "password", "octorig", "letmein", "123456"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg2://octorig:octorig@localhost:5432/octorig"

    # Security
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Debug mode — enables /docs, /redoc, verbose errors. Never True in production.
    debug: bool = False

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

    # Marketplace — comma-separated hex-encoded Ed25519 public keys.
    # Leave empty to disable marketplace package installation entirely.
    marketplace_trusted_keys: str = ""

    def get_marketplace_trusted_keys(self) -> list[str]:
        return [k.strip() for k in self.marketplace_trusted_keys.split(",") if k.strip()]

    # ── Startup safety validators ──────────────────────────────────────────────

    @field_validator("secret_key")
    @classmethod
    def _require_strong_secret(cls, v: str) -> str:
        if v in _INSECURE_SECRETS or len(v) < 32:
            raise ValueError(
                "SECRET_KEY is insecure. Set it to a random string of at least 32 characters "
                "(e.g. openssl rand -hex 32). See .env.example."
            )
        return v

    @field_validator("admin_password")
    @classmethod
    def _require_strong_admin_password(cls, v: str) -> str:
        if v.lower() in _INSECURE_PASSWORDS:
            raise ValueError(
                f"ADMIN_PASSWORD '{v}' is a known-weak default. "
                "Set a strong password in your .env file."
            )
        return v


settings = Settings()
