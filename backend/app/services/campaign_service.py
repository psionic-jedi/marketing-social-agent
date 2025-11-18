"""
Campaign service - Business logic for managing campaigns.

Handles:
- Campaign creation and execution
- Database persistence
- Background task coordination
"""
import logging
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.database import Campaign, CampaignStatus, CampaignResult, AgentExecution, AgentStatus
from app.agents.state import create_initial_state
from app.agents.overlord import OverlordAgent

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing marketing campaigns."""

    def __init__(self):
        self.overlord = OverlordAgent()

    async def execute_campaign(self, campaign_id: uuid.UUID, db: Session) -> dict:
        """
        Execute a marketing campaign workflow.

        Args:
            campaign_id: UUID of the campaign to execute
            db: Database session

        Returns:
            Dictionary with execution results
        """
        logger.info(f"Starting campaign execution for {campaign_id}")

        # Get campaign from database
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        try:
            # Update campaign status
            campaign.status = CampaignStatus.RUNNING
            db.commit()

            # Create initial state
            initial_state = create_initial_state(
                campaign_id=str(campaign.id),
                category_url=campaign.category_url,
                budget=float(campaign.budget) if campaign.budget else None,
                launch_date=campaign.launch_date.isoformat() if campaign.launch_date else None
            )

            # Execute workflow
            logger.info(f"Executing Overlord workflow for campaign {campaign_id}")
            final_state = await self.overlord.execute_async(initial_state)

            # Save results to database
            await self._save_results(campaign_id, final_state, db)

            # Update campaign status
            if final_state.get("errors"):
                campaign.status = CampaignStatus.PARTIAL
            else:
                campaign.status = CampaignStatus.COMPLETED

            campaign.completed_at = datetime.utcnow()
            db.commit()

            logger.info(f"Campaign {campaign_id} execution completed")

            return {
                "campaign_id": str(campaign_id),
                "status": campaign.status.value,
                "final_state": final_state
            }

        except Exception as e:
            logger.error(f"Campaign {campaign_id} execution failed: {e}", exc_info=True)

            # Update campaign status to failed
            campaign.status = CampaignStatus.FAILED
            campaign.completed_at = datetime.utcnow()
            db.commit()

            raise

    async def _save_results(
        self,
        campaign_id: uuid.UUID,
        final_state: dict,
        db: Session
    ) -> None:
        """
        Save campaign results to database.

        Args:
            campaign_id: Campaign ID
            final_state: Final state from workflow
            db: Database session
        """
        logger.info(f"Saving results for campaign {campaign_id}")

        # Create or update campaign result
        result = db.query(CampaignResult).filter(
            CampaignResult.campaign_id == campaign_id
        ).first()

        if not result:
            result = CampaignResult(campaign_id=campaign_id)
            db.add(result)

        # Save outputs from each agent
        result.research_data = final_state.get("research_data")
        result.content_outputs = final_state.get("content_outputs")
        result.social_media_plan = final_state.get("social_media_plan")
        result.ppc_campaign = final_state.get("ppc_campaign")
        result.crm_plan = final_state.get("crm_plan")
        result.analyst_insights = final_state.get("analyst_insights")

        # Log agent executions
        await self._log_agent_executions(campaign_id, final_state, db)

        db.commit()
        logger.info(f"Results saved for campaign {campaign_id}")

    async def _log_agent_executions(
        self,
        campaign_id: uuid.UUID,
        final_state: dict,
        db: Session
    ) -> None:
        """
        Log individual agent executions.

        Args:
            campaign_id: Campaign ID
            final_state: Final state with execution details
            db: Database session
        """
        # Log Research Agent
        if final_state.get("research_data"):
            execution = AgentExecution(
                campaign_id=campaign_id,
                agent_name="research",
                status=AgentStatus.COMPLETED,
                started_at=datetime.fromisoformat(final_state.get("started_at")),
                completed_at=datetime.utcnow(),
                output={"data": "Research completed"},
                errors=None
            )
            db.add(execution)

        # Log Content Agent
        if final_state.get("content_outputs"):
            execution = AgentExecution(
                campaign_id=campaign_id,
                agent_name="content",
                status=AgentStatus.COMPLETED,
                started_at=datetime.fromisoformat(final_state.get("started_at")),
                completed_at=datetime.utcnow(),
                output={"data": "Content generated"},
                errors=None
            )
            db.add(execution)

        # Log any errors
        if final_state.get("errors"):
            for error in final_state.get("errors", []):
                execution = AgentExecution(
                    campaign_id=campaign_id,
                    agent_name="unknown",
                    status=AgentStatus.FAILED,
                    started_at=datetime.fromisoformat(final_state.get("started_at")),
                    completed_at=datetime.utcnow(),
                    output=None,
                    errors={"error": error}
                )
                db.add(execution)
