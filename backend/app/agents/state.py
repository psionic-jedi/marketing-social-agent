"""
LangGraph state definition for the marketing campaign workflow.
This state is shared across all agents in the workflow.
"""
from typing import TypedDict, Dict, List, Optional, Annotated
from datetime import datetime
import operator


class MarketingCampaignState(TypedDict):
    """
    State for the marketing campaign generation workflow.

    This state is passed between all agents and accumulates results
    as the workflow progresses.
    """

    # Input from user
    campaign_id: str
    category_url: str
    budget: Optional[float]
    launch_date: Optional[str]

    # Research Phase Output
    research_data: Optional[Dict]  # From Research Agent
    # {
    #   "products": [...],
    #   "category_insights": {...},
    #   "parent_questions": [...],
    #   "competitor_insights": {...},
    #   "seo_keywords": {...}
    # }

    # Content Phase Output
    content_outputs: Optional[Dict]  # From Content Agent
    # {
    #   "hero_section": {...},
    #   "features": [...],
    #   "category_description": str,
    #   "meta_title": str,
    #   "meta_description": str
    # }

    generated_images: Annotated[List[str], operator.add]  # URLs to generated images
    # Will accumulate images as they're generated

    # Marketing Channels
    social_media_plan: Optional[Dict]
    ppc_campaign: Optional[Dict]  # Google Ads
    meta_ads_campaign: Optional[Dict]  # Facebook/Instagram Ads
    crm_plan: Optional[Dict]

    # Analysis
    analyst_insights: Optional[Dict]

    # System metadata
    current_step: str  # Current agent being executed
    progress_percentage: int  # 0-100
    errors: Annotated[List[str], operator.add]  # Accumulate errors
    started_at: Optional[str]  # ISO timestamp
    completed_at: Optional[str]  # ISO timestamp

    # Final consolidated output
    final_campaign: Optional[Dict]


def create_initial_state(
    campaign_id: str,
    category_url: str,
    budget: Optional[float] = None,
    launch_date: Optional[str] = None
) -> MarketingCampaignState:
    """
    Create initial state for a new campaign.

    Args:
        campaign_id: UUID of the campaign
        category_url: URL of the category page to analyze
        budget: Optional campaign budget
        launch_date: Optional launch date

    Returns:
        Initial MarketingCampaignState
    """
    return MarketingCampaignState(
        campaign_id=campaign_id,
        category_url=category_url,
        budget=budget,
        launch_date=launch_date,
        research_data=None,
        content_outputs=None,
        generated_images=[],
        social_media_plan=None,
        ppc_campaign=None,
        meta_ads_campaign=None,
        crm_plan=None,
        analyst_insights=None,
        current_step="initializing",
        progress_percentage=0,
        errors=[],
        started_at=datetime.utcnow().isoformat(),
        completed_at=None,
        final_campaign=None
    )
