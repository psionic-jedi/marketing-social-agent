"""
API routes for the marketing agent system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
import logging

from app.core.database import get_db_session
from app.models.database import Campaign, CampaignStatus, CampaignResult, GeneratedArticle, ApiUsageLog
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.services.article_generator import ArticleGenerator
from app.tasks.campaign_tasks import execute_campaign_task
from sqlalchemy import func

router = APIRouter()
logger = logging.getLogger(__name__)


class ArticleGenerateRequest(BaseModel):
    """Request body for article generation."""
    content_idea_id: str
    title: str
    intro: str
    type: str
    key_topics: List[str]
    target_audience: str
    seo_keywords: Optional[List[str]] = None


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db_session)
):
    """
    Create a new marketing campaign.

    This endpoint accepts a category URL and optional parameters,
    then initiates the multi-agent workflow via Celery task queue.
    Tasks survive laptop sleep, restarts, and network interruptions.
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

    logger.info(f"Campaign {campaign.id} created, queuing Celery task")

    # Queue the campaign execution task in Celery
    # This task is persisted in Redis and survives restarts
    task = execute_campaign_task.delay(str(campaign.id))
    logger.info(f"Campaign {campaign.id} queued as Celery task {task.id}")

    return campaign


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
            "meta_ads_campaign": results.meta_ads_campaign,
            "crm_plan": results.crm_plan,
            "analyst_insights": results.analyst_insights
        }
    }


@router.post("/campaigns/{campaign_id}/generate-article")
async def generate_article(
    campaign_id: uuid.UUID,
    request: ArticleGenerateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Generate a full article based on a content idea.

    Takes a content idea from the research phase and generates a complete
    SEO-optimized article with meta description, headers, and full body content.
    """
    logger.info(f"Generating article for campaign {campaign_id}, idea: {request.content_idea_id}")

    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Get campaign results for context
    results = db.query(CampaignResult).filter(
        CampaignResult.campaign_id == campaign_id
    ).first()

    if not results or not results.research_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign has no research data to base article on"
        )

    # Generate the article
    try:
        article_generator = ArticleGenerator(db=db, campaign_id=str(campaign_id))
        article = await article_generator.generate_full_article(
            title=request.title,
            intro=request.intro,
            article_type=request.type,
            key_topics=request.key_topics,
            target_audience=request.target_audience,
            seo_keywords=request.seo_keywords or [],
            category_name=results.research_data.get("category_insights", {}).get("category_name", ""),
            products=results.research_data.get("products", [])[:10]
        )

        # Save to database (upsert - replace if same content_idea_id exists)
        existing = db.query(GeneratedArticle).filter(
            GeneratedArticle.campaign_id == campaign_id,
            GeneratedArticle.content_idea_id == request.content_idea_id
        ).first()

        if existing:
            existing.article_data = article
            existing.created_at = __import__('datetime').datetime.utcnow()
        else:
            generated = GeneratedArticle(
                campaign_id=campaign_id,
                content_idea_id=request.content_idea_id,
                article_data=article
            )
            db.add(generated)

        db.commit()

        logger.info(f"Article generated and saved for campaign {campaign_id}")
        return {
            "success": True,
            "content_idea_id": request.content_idea_id,
            "article": article
        }

    except Exception as e:
        logger.error(f"Error generating article: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate article: {str(e)}"
        )


@router.get("/campaigns/{campaign_id}/articles")
async def get_campaign_articles(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    """
    Get all generated articles for a campaign.
    Returns a dict keyed by content_idea_id for easy lookup.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    articles = db.query(GeneratedArticle).filter(
        GeneratedArticle.campaign_id == campaign_id
    ).all()

    return {
        a.content_idea_id: {
            "article": a.article_data,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in articles
    }


@router.get("/campaigns/{campaign_id}/costs")
async def get_campaign_costs(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db_session)
):
    """
    Get API usage costs for a campaign.

    Returns per-agent breakdown and totals, plus individual call records.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Get all usage logs for this campaign
    logs = db.query(ApiUsageLog).filter(
        ApiUsageLog.campaign_id == campaign_id
    ).order_by(ApiUsageLog.created_at).all()

    if not logs:
        return {
            "campaign_id": str(campaign_id),
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "by_agent": [],
            "records": []
        }

    # Aggregate by agent
    agent_stats = db.query(
        ApiUsageLog.agent_name,
        func.count(ApiUsageLog.id).label("calls"),
        func.sum(ApiUsageLog.input_tokens).label("input_tokens"),
        func.sum(ApiUsageLog.output_tokens).label("output_tokens"),
        func.sum(ApiUsageLog.estimated_cost_usd).label("cost"),
    ).filter(
        ApiUsageLog.campaign_id == campaign_id
    ).group_by(ApiUsageLog.agent_name).all()

    by_agent = [
        {
            "agent_name": row.agent_name,
            "calls": row.calls,
            "input_tokens": row.input_tokens or 0,
            "output_tokens": row.output_tokens or 0,
            "cost_usd": round(float(row.cost or 0), 4),
        }
        for row in agent_stats
    ]

    # Build individual records
    records = [
        {
            "agent_name": log.agent_name,
            "call_type": log.call_type,
            "model": log.model,
            "input_tokens": log.input_tokens,
            "output_tokens": log.output_tokens,
            "cost_usd": round(float(log.estimated_cost_usd or 0), 6),
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]

    total_input = sum(a["input_tokens"] for a in by_agent)
    total_output = sum(a["output_tokens"] for a in by_agent)
    total_cost = sum(a["cost_usd"] for a in by_agent)
    total_calls = sum(a["calls"] for a in by_agent)

    return {
        "campaign_id": str(campaign_id),
        "total_calls": total_calls,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost_usd": round(total_cost, 4),
        "by_agent": by_agent,
        "records": records,
    }
