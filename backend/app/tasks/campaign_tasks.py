"""
Celery tasks for campaign execution.

These tasks run in a Celery worker process, separate from the FastAPI server.
They survive laptop sleep, restarts, and network interruptions.
"""
import asyncio
import logging
import uuid

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.services.campaign_service import CampaignService
from app.models.database import Campaign, CampaignStatus

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="execute_campaign",
    max_retries=1,
    soft_time_limit=3600,  # 1 hour soft limit
    time_limit=3900,       # 1 hour 5 min hard limit
)
def execute_campaign_task(self, campaign_id: str):
    """
    Execute a marketing campaign workflow.

    This task is queued in Redis and executed by a Celery worker.
    It survives server restarts and laptop sleep.

    Args:
        campaign_id: UUID string of the campaign to execute
    """
    logger.info(f"Celery task starting: Campaign {campaign_id}")

    # Create a fresh database session for this task
    with get_db() as db:
        try:
            # Verify campaign exists and is in correct state
            campaign = db.query(Campaign).filter(
                Campaign.id == uuid.UUID(campaign_id)
            ).first()

            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return {"status": "error", "message": "Campaign not found"}

            # Skip if already completed or failed
            if campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.FAILED]:
                logger.warning(f"Campaign {campaign_id} already {campaign.status.value}, skipping")
                return {"status": "skipped", "message": f"Campaign already {campaign.status.value}"}

            # Execute the campaign workflow
            campaign_service = CampaignService()

            # Run the async execute_campaign in an event loop
            # Celery tasks are synchronous, so we need to run the async code
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    campaign_service.execute_campaign(uuid.UUID(campaign_id), db)
                )
                logger.info(f"Celery task completed: Campaign {campaign_id}")
                return {"status": "success", "result": result}
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Celery task failed: Campaign {campaign_id}: {e}", exc_info=True)

            # Update campaign status to FAILED if possible
            try:
                campaign = db.query(Campaign).filter(
                    Campaign.id == uuid.UUID(campaign_id)
                ).first()
                if campaign and campaign.status not in [CampaignStatus.COMPLETED, CampaignStatus.FAILED]:
                    campaign.status = CampaignStatus.FAILED
                    db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update campaign status: {db_error}")

            # Re-raise to let Celery handle retry logic
            raise
