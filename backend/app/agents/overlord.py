"""
Overlord Agent - Master orchestrator for the marketing campaign workflow.

Uses LangGraph to coordinate the execution of all agents in the correct sequence.
"""
import logging
from datetime import datetime
from langgraph.graph import StateGraph, END
from typing import Dict

from app.agents.state import MarketingCampaignState
from app.agents.research_agent import ResearchAgent
from app.agents.content_agent import ContentAgent

logger = logging.getLogger(__name__)


class OverlordAgent:
    """
    Overlord agent that orchestrates the entire marketing campaign workflow.

    Coordinates:
    - Research Agent
    - Content Agent
    - (Future: Social Media, PPC, CRM, Analyst agents)
    """

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for campaign generation.

        Returns:
            Compiled StateGraph workflow
        """
        # Create workflow graph
        workflow = StateGraph(MarketingCampaignState)

        # Add nodes for each agent
        workflow.add_node("research", self._run_research_agent)
        workflow.add_node("content", self._run_content_agent)
        workflow.add_node("finalize", self._finalize_campaign)

        # Define the flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "finalize")
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

        try:
            state = self.content_agent.execute(state)
        except Exception as e:
            error_msg = f"Content Agent execution failed: {str(e)}"
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
        state["progress_percentage"] = 90

        # Compile final campaign package
        final_campaign = {
            "campaign_id": state["campaign_id"],
            "category_url": state["category_url"],
            "research": state.get("research_data"),
            "content": state.get("content_outputs"),
            "images": state.get("generated_images", []),
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
