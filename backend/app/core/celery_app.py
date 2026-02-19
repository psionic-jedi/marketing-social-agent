"""
Celery application configuration.

Uses Redis as both broker and result backend for task persistence.
Tasks survive laptop sleep, restarts, and network interruptions.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "marketing_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.campaign_tasks"],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Task behavior
    task_track_started=True,  # Track when tasks start
    task_acks_late=True,      # Re-queue if worker dies mid-task
    task_reject_on_worker_lost=True,  # Reject task if worker is killed

    # Worker behavior
    worker_prefetch_multiplier=1,  # One task at a time per worker

    # Result expiration (24 hours)
    result_expires=86400,

    # Timezone
    timezone="UTC",
    enable_utc=True,
)
