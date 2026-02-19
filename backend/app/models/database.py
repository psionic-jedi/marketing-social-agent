"""
Database models for the marketing agent system.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, DateTime, Numeric, Date, Text,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class CampaignStatus(str, enum.Enum):
    """Campaign execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class AgentStatus(str, enum.Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AssetType(str, enum.Enum):
    """Type of generated asset."""
    IMAGE = "image"
    HTML = "html"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"
    JSON = "json"


class Campaign(Base):
    """Campaign table - main entity for marketing campaigns."""
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    category_url = Column(Text, nullable=False)
    category_name = Column(String(255))
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    budget = Column(Numeric(10, 2))
    launch_date = Column(Date)

    # Progress tracking fields
    current_step = Column(String(100))  # Current agent being executed
    progress_percentage = Column(Numeric(5, 2), default=0)  # 0-100

    # Relationships
    agent_executions = relationship("AgentExecution", back_populates="campaign", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="campaign", cascade="all, delete-orphan")
    results = relationship("CampaignResult", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    generated_articles = relationship("GeneratedArticle", back_populates="campaign", cascade="all, delete-orphan")
    bi_reports = relationship("BIReport", back_populates="campaign", cascade="all, delete-orphan")


class AgentExecution(Base):
    """Agent execution tracking - records each agent's execution."""
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.PENDING)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    output = Column(JSONB)
    errors = Column(JSONB)

    # Relationships
    campaign = relationship("Campaign", back_populates="agent_executions")


class Asset(Base):
    """Generated assets - images, HTML, CSV files, etc."""
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    file_url = Column(Text, nullable=False)
    asset_metadata = Column(JSONB)  # renamed from 'metadata' - reserved word in SQLAlchemy
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="assets")


class CampaignResult(Base):
    """Campaign results - consolidated output from all agents."""
    __tablename__ = "campaign_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False, unique=True)
    research_data = Column(JSONB)
    content_outputs = Column(JSONB)
    social_media_plan = Column(JSONB)
    ppc_campaign = Column(JSONB)
    meta_ads_campaign = Column(JSONB)
    crm_plan = Column(JSONB)
    analyst_insights = Column(JSONB)

    # Relationships
    campaign = relationship("Campaign", back_populates="results")


class GeneratedArticle(Base):
    """Generated articles - persisted so users can view them after navigating away."""
    __tablename__ = "generated_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    content_idea_id = Column(String(255), nullable=False)
    article_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="generated_articles")


class BIReport(Base):
    """BI reports uploaded for analysis by the Analyst Agent."""
    __tablename__ = "bi_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    file_url = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    analysis_result = Column(JSONB)

    # Relationships
    campaign = relationship("Campaign", back_populates="bi_reports")
