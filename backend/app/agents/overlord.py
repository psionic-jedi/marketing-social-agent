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
    - CRM Agent: Email marketing campaigns with MJML
    - Analyst Agent: Performance analysis and recommendations
    """

    def __init__(self, progress_callback=None):
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.social_media_agent = SocialMediaAgent()
        self.ppc_agent = PPCAgent()
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
        workflow.add_node("crm", self._run_crm_agent)
        workflow.add_node("analyst", self._run_analyst_agent)
        workflow.add_node("finalize", self._finalize_campaign)

        # Define the sequential flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "social_media")
        workflow.add_edge("social_media", "ppc")
        workflow.add_edge("ppc", "crm")
        workflow.add_edge("crm", "analyst")
        workflow.add_edge("analyst", "finalize")
        workflow.add_edge("finalize", END)

        # Compile the workflow
        return workflow.compile()

    def _run_research_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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
            state = self.research_agent.execute(state)
        except Exception as e:
            error_msg = f"Research Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    def _run_content_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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

    def _run_social_media_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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

    def _run_ppc_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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
            self.progress_callback(state['campaign_id'], 'ppc', 66.67)

        try:
            state = self.ppc_agent.execute(state)
        except Exception as e:
            error_msg = f"PPC Agent execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)

        return state

    def _run_crm_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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

    def _run_analyst_agent(self, state: MarketingCampaignState) -> MarketingCampaignState:
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

    def _finalize_campaign(self, state: MarketingCampaignState) -> MarketingCampaignState:
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

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the entire campaign workflow.

        Args:
            state: Initial campaign state

        Returns:
            Final state with all outputs
        """
        logger.info(f"Overlord: Starting workflow for campaign {state['campaign_id']}")

        try:
            # Run the workflow
            final_state = self.workflow.invoke(state)
            return final_state

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["current_step"] = "failed"
            state["progress_percentage"] = 100
            state["completed_at"] = datetime.utcnow().isoformat()
            return state

    async def execute_async(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the workflow asynchronously (for background tasks).

        Args:
            state: Initial campaign state

        Returns:
            Final state with all outputs
        """
        # For now, just call the sync version
        # In a production system, we'd use LangGraph's async support
        return self.execute(state)
