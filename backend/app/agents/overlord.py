"""
Overlord Agent - Master orchestrator for the marketing campaign workflow.

Uses LangGraph to coordinate the execution of all agents in the correct sequence.
"""
import logging
from datetime import datetime
from langgraph.graph import StateGraph, END
from typing import Dict
import uuid

from app.agents.state import MarketingCampaignState
from app.agents.research_agent import ResearchAgent
from app.agents.content_agent import ContentAgent
from app.agents.social_media_agent import SocialMediaAgent
from app.agents.ppc_agent import PPCAgent
from app.agents.meta_ads_agent import MetaAdsAgent
from app.agents.crm_agent import CRMAgent
from app.agents.analyst_agent import AnalystAgent

logger = logging.getLogger(__name__)


class OverlordAgent:
    """
    Overlord agent that orchestrates the entire marketing campaign workflow.

    Coordinates:
    - Research Agent: Product and market intelligence
    - Content Agent: Marketing copy and image generation
    - Social Media Agent: Social media strategy and content
    - PPC Agent: Google Ads campaigns
    - Meta Ads Agent: Facebook and Instagram campaigns
    - CRM Agent: Email marketing campaigns with MJML
    - Analyst Agent: Performance analysis and recommendations
    """

    def __init__(self, progress_callback=None, cost_tracker=None):
        self.research_agent = ResearchAgent(progress_callback=progress_callback, cost_tracker=cost_tracker)
        self.content_agent = ContentAgent(cost_tracker=cost_tracker)
        self.social_media_agent = SocialMediaAgent(cost_tracker=cost_tracker)
        self.ppc_agent = PPCAgent(cost_tracker=cost_tracker)
        self.meta_ads_agent = MetaAdsAgent(cost_tracker=cost_tracker)
        self.crm_agent = CRMAgent()
        self.analyst_agent = AnalystAgent()
        self.progress_callback = progress_callback
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for campaign generation.

        Returns:
            Compiled StateGraph workflow
        """
        # Create workflow graph
        workflow = StateGraph(MarketingCampaignState)

        # Add nodes for all agents
        workflow.add_node("research", self._run_research_agent)
        workflow.add_node("content", self._run_content_agent)
        workflow.add_node("social_media", self._run_social_media_agent)
        workflow.add_node("ppc", self._run_ppc_agent)
        workflow.add_node("meta_ads", self._run_meta_ads_agent)
        workflow.add_node("crm", self._run_crm_agent)
        workflow.add_node("analyst", self._run_analyst_agent)
        workflow.add_node("finalize", self._finalize_campaign)

        # Define the sequential flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "social_media")
        workflow.add_edge("social_media", "ppc")
        workflow.add_edge("ppc", "meta_ads")
        workflow.add_edge("meta_ads", "crm")
        workflow.add_edge("crm", "analyst")
        workflow.add_edge("analyst", "finalize")
        workflow.add_edge("finalize", END)

        # Compile the workflow
        return workflow.compile()

    async def _run_research_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the Research Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with research data
        """
        logger.info(f"Overlord: Executing Research Agent for campaign {state['campaign_id']}")

        # Update progress: Starting research
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'research', 16.67)

        try:
            state = await self.research_agent.execute(state)
        except Exception as e:
            error_msg = f"Research Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_content_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the Content Agent.

        Args:
            state: Current campaign state with research data

        Returns:
            Updated state with content and images
        """
        logger.info(f"Overlord: Executing Content Agent for campaign {state['campaign_id']}")

        # Update progress: Starting content generation
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'content', 33.33)

        try:
            state = self.content_agent.execute(state)
        except Exception as e:
            error_msg = f"Content Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_social_media_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the Social Media Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with social media plan
        """
        logger.info(f"Overlord: Executing Social Media Agent for campaign {state['campaign_id']}")

        # Update progress: Starting social media planning
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'social_media', 50.0)

        try:
            state = self.social_media_agent.execute(state)
        except Exception as e:
            error_msg = f"Social Media Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_ppc_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the PPC Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with PPC campaign
        """
        logger.info(f"Overlord: Executing PPC Agent for campaign {state['campaign_id']}")

        # Update progress: Starting PPC campaign creation
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'ppc', 60.0)

        try:
            state = self.ppc_agent.execute(state)
        except Exception as e:
            error_msg = f"PPC Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_meta_ads_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the Meta Ads Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with Meta Ads campaign
        """
        logger.info(f"Overlord: Executing Meta Ads Agent for campaign {state['campaign_id']}")

        # Update progress: Starting Meta Ads campaign creation
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'meta_ads', 70.0)

        try:
            state = self.meta_ads_agent.execute(state)
        except Exception as e:
            error_msg = f"Meta Ads Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_crm_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the CRM Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with CRM plan
        """
        logger.info(f"Overlord: Executing CRM Agent for campaign {state['campaign_id']}")

        # Update progress: Starting CRM planning
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'crm', 83.33)

        try:
            state = self.crm_agent.execute(state)
        except Exception as e:
            error_msg = f"CRM Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _run_analyst_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Run the Analyst Agent.

        Args:
            state: Current campaign state

        Returns:
            Updated state with analyst insights
        """
        logger.info(f"Overlord: Executing Analyst Agent for campaign {state['campaign_id']}")

        # Update progress: Starting analysis
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'analyst', 90.0)

        try:
            state = self.analyst_agent.execute(state)
        except Exception as e:
            error_msg = f"Analyst Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    async def _finalize_campaign(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Finalize the campaign by consolidating all outputs.

        Args:
            state: Current campaign state with all agent outputs

        Returns:
            Updated state with final_campaign compiled
        """
        logger.info(f"Overlord: Finalizing campaign {state['campaign_id']}")

        state["current_step"] = "finalizing"
        state["progress_percentage"] = 95

        # Update progress: Finalizing
        if self.progress_callback:
            self.progress_callback(state['campaign_id'], 'finalizing', 95.0)

        # Compile final campaign package with all agent outputs
        final_campaign = {
            "campaign_id": state["campaign_id"],
            "category_url": state["category_url"],
            "budget": state.get("budget"),
            "research": state.get("research_data"),
            "content": state.get("content_outputs"),
            "images": state.get("generated_images", []),
            "social_media": state.get("social_media_plan"),
            "ppc": state.get("ppc_campaign"),
            "meta_ads": state.get("meta_ads_campaign"),
            "crm": state.get("crm_plan"),
            "analyst": state.get("analyst_insights"),
            "execution_summary": {
                "started_at": state.get("started_at"),
                "completed_at": datetime.utcnow().isoformat(),
                "total_errors": len(state.get("errors", [])),
                "errors": state.get("errors", [])
            }
        }

        state["final_campaign"] = final_campaign
        state["completed_at"] = datetime.utcnow().isoformat()
        state["progress_percentage"] = 100
        state["current_step"] = "completed"

        logger.info(f"Campaign {state['campaign_id']} completed successfully")

        return state

    async def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the entire campaign workflow asynchronously.

        Args:
            state: Initial campaign state

        Returns:
            Final state with all outputs
        """
        logger.info(f"Overlord: Starting workflow for campaign {state['campaign_id']}")

        try:
            # Run agents sequentially (for now, bypassing LangGraph for async support)
            # Step 1: Research
            state = await self._run_research_agent(state)

            # Step 2: Content
            state = await self._run_content_agent(state)

            # Step 3: Social Media
            state = await self._run_social_media_agent(state)

            # Step 4: PPC (Google Ads)
            state = await self._run_ppc_agent(state)

            # Step 5: Meta Ads (Facebook/Instagram)
            state = await self._run_meta_ads_agent(state)

            # Step 6: CRM
            state = await self._run_crm_agent(state)

            # Step 7: Analyst
            state = await self._run_analyst_agent(state)

            # Finalize
            state = await self._finalize_campaign(state)

            return state

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["current_step"] = "failed"
            state["progress_percentage"] = 100
            state["completed_at"] = datetime.utcnow().isoformat()
            return state
