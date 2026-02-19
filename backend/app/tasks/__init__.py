"""
Celery tasks package.

This package contains async tasks that are executed by Celery workers.
Tasks are queued in Redis and survive restarts, sleep, and network interruptions.
"""
from app.tasks.campaign_tasks import execute_campaign_task

__all__ = ["execute_campaign_task"]
