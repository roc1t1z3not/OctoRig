import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.ws.manager import manager
    manager.set_loop(asyncio.get_running_loop())
    _run_migrations()
    _seed_admin()
    _seed_badges()
    _sync_labs()      # upserts lab templates + any inline challenges
    _load_plugins(app)
    yield


def _run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def _load_plugins(app: FastAPI) -> None:
    from app.database import SessionLocal
    from app.plugins.registry import discover_plugins, mount_plugins

    discover_plugins()
    mount_plugins(app, SessionLocal)


def _seed_badges() -> None:
    from app.database import SessionLocal
    from app.services.achievement_service import seed_badge_catalog

    db = SessionLocal()
    try:
        seed_badge_catalog(db)
    finally:
        db.close()


def _sync_labs() -> None:
    from app.database import SessionLocal
    from app.services.lab_service import sync_registry

    db = SessionLocal()
    try:
        sync_registry(db)
    finally:
        db.close()


def _seed_admin() -> None:
    from app.core.security import hash_password
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.team_service import ensure_personal_team

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                is_active=True,
                is_superuser=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            ensure_personal_team(db, admin)
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="OctoRig Platform API",
        version="3.0.0",
        description="Offensive security training platform — labs, CTF events, challenges, badges",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.api.events_ws import router as ws_router
    from app.api.admin import router as admin_router
    from app.api.api_keys import router as api_keys_router
    from app.api.auth import router as auth_router
    from app.api.badges import router as badges_router
    from app.api.challenges import router as challenges_router
    from app.api.content import router as content_router
    from app.api.marketplace import router as marketplace_router
    from app.api.notifications import router as notifications_router
    from app.api.profiles import router as profiles_router
    from app.api.deployments import router as deployments_router
    from app.api.events import router as events_router
    from app.api.labs import router as labs_router
    from app.api.scheduler import router as scheduler_router
    from app.api.scoreboards import router as scoreboards_router
    from app.api.system import router as system_router
    from app.api.teams import invitations_router, router as teams_router

    app.include_router(ws_router)          # /ws/events (no prefix — raw WS path)
    prefix = "/api/v1"
    app.include_router(auth_router, prefix=prefix)
    app.include_router(labs_router, prefix=prefix)
    app.include_router(deployments_router, prefix=prefix)
    app.include_router(system_router, prefix=prefix)
    app.include_router(teams_router, prefix=prefix)
    app.include_router(invitations_router, prefix=prefix)
    app.include_router(api_keys_router, prefix=prefix)
    app.include_router(scheduler_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(challenges_router, prefix=prefix)
    app.include_router(scoreboards_router, prefix=prefix)
    app.include_router(events_router, prefix=prefix)
    app.include_router(badges_router, prefix=prefix)
    app.include_router(profiles_router, prefix=prefix)
    app.include_router(notifications_router, prefix=prefix)
    app.include_router(content_router, prefix=prefix)
    app.include_router(marketplace_router, prefix=prefix)

    return app


app = create_app()
