from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "octorig",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    beat_schedule={
        "dispatch-due-scheduled-actions": {
            "task": "app.worker.tasks.dispatch_due_actions",
            "schedule": 60.0,
        },
        "auto-destroy-dynamic-labs": {
            "task": "app.worker.tasks.auto_destroy_dynamic_labs",
            "schedule": 60.0,
        },
    },
)
