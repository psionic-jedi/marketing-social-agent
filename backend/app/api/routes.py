"""
API routes for the marketing agent system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
import logging

from app.core.database import get_db_session
from app.models.database import Campaign, CampaignStatus, CampaignResult
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.services.campaign_service import CampaignService

router = APIRouter()
logger = logging.getLogger(__name__)
campaign_service = CampaignService()


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """
    Create a new marketing campaign.

    This endpoint accepts a category URL and optional parameters,
    then initiates the multi-agent workflow to generate a complete
    marketing campaign in the background.
    """
    logger.info(f"Creating new campaign for URL: {campaign_data.category_url}")

    # Create new campaign
    campaign = Campaign(
        user_id=uuid.uuid4(),  # TODO: Get from authentication
        category_url=str(campaign_data.category_url),  # Convert Pydantic URL to string
        budget=campaign_data.budget,
        launch_date=campaign_data.launch_date,
        status=CampaignStatus.PENDING
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    logger.info(f"Campaign {campaign.id} created, triggering workflow")

    # Trigger workflow execution in background
    background_tasks.add_task(
        execute_campaign_workflow,
        campaign.id,
        db
    )

    return campaign


async def execute_campaign_workflow(campaign_id: uuid.UUID, db: Session):
    """
    Background task to execute the campaign workflow.

    Args:
        campaign_id: ID of the campaign to execute
        db: Database session
    """
    try:
        logger.info(f"Background task: Executing campaign {campaign_id}")
        await campaign_service.execute_campaign(campaign_id, db)
        logger.info(f"Background task: Campaign {campaign_id} execution completed")
    except Exception as e:
        logger.error(f"Background task: Campaign {campaign_id} failed: {e}", exc_info=True)


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    List all campaigns for the current user.
    """
    # TODO: Filter by authenticated user_id
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    """
    Get details of a specific campaign.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    """
    Delete a campaign and all associated data.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    db.delete(campaign)
    db.commit()

    return None


@router.get("/campaigns/{campaign_id}/results")
async def get_campaign_results(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    """
    Get the generated results for a campaign.

    Returns research data, content, images, and all generated assets.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Get campaign results
    results = db.query(CampaignResult).filter(
        CampaignResult.campaign_id == campaign_id
    ).first()

    if not results:
        # Campaign exists but no results yet (still running or failed)
        return {
            "campaign_id": str(campaign_id),
            "status": campaign.status.value,
            "message": "Campaign is still processing or has not completed yet",
            "results": None
        }

    return {
        "campaign_id": str(campaign_id),
        "category_url": campaign.category_url,
        "status": campaign.status.value,
        "created_at": campaign.created_at.isoformat(),
        "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None,
        "results": {
            "research_data": results.research_data,
            "content_outputs": results.content_outputs,
            "social_media_plan": results.social_media_plan,
            "ppc_campaign": results.ppc_campaign,
            "crm_plan": results.crm_plan,
            "analyst_insights": results.analyst_insights
        }
    }
