"""
Pydantic schemas for campaign-related requests and responses.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""
    category_url: HttpUrl = Field(..., description="URL of the category page to generate campaign for")
    budget: Optional[Decimal] = Field(None, ge=0, description="Campaign budget (optional)")
    launch_date: Optional[date] = Field(None, description="Planned launch date (optional)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "category_url": "https://yourstore.com/baby-sleepsuits",
                "budget": 5000.00,
                "launch_date": "2025-12-01"
            }]
        }
    }


class CampaignResponse(BaseModel):
    """Schema for campaign response."""
    id: UUID
    user_id: UUID
    category_url: str
    category_name: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    budget: Optional[Decimal]
    launch_date: Optional[date]

    model_config = {
        "from_attributes": True
    }


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    category_name: Optional[str] = None
    budget: Optional[Decimal] = None
    launch_date: Optional[date] = None
