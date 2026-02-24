"""
Cost Tracker - Tracks Anthropic API usage and estimated costs per campaign.

Provides:
- In-memory accumulation during campaign execution (CostTracker)
- Bulk flush to database at end of campaign
- Single-call save for standalone usage (article generation)
- Cost calculation based on model pricing
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.database import ApiUsageLog

logger = logging.getLogger(__name__)

# Pricing per million tokens (USD) as of 2025
MODEL_PRICING = {
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.0},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
}

# Fallback for unknown models
DEFAULT_PRICING = {"input": 3.0, "output": 15.0}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost in USD for a single API call."""
    pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)


class CostTracker:
    """
    Accumulates API usage records in memory during campaign execution,
    then flushes them to the database in bulk.
    """

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self._records: List[dict] = []

    def record(self, response, agent_name: str, call_type: str) -> None:
        """
        Record usage from an Anthropic API response.

        Args:
            response: The Anthropic messages.create() response object
            agent_name: Which agent made the call (e.g. "research", "content")
            call_type: What type of call (e.g. "extract_product_detail", "generate_hero")
        """
        try:
            usage = response.usage
            model = response.model
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            cost = calculate_cost(model, input_tokens, output_tokens)

            self._records.append({
                "campaign_id": self.campaign_id,
                "agent_name": agent_name,
                "call_type": call_type,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost_usd": cost,
            })
        except Exception as e:
            logger.warning(f"CostTracker.record failed (non-fatal): {e}")

    def flush(self, db: Session) -> int:
        """
        Bulk-insert all accumulated records to the database.

        Returns:
            Number of records flushed
        """
        if not self._records:
            return 0

        try:
            logs = [
                ApiUsageLog(
                    campaign_id=uuid.UUID(r["campaign_id"]),
                    agent_name=r["agent_name"],
                    call_type=r["call_type"],
                    model=r["model"],
                    input_tokens=r["input_tokens"],
                    output_tokens=r["output_tokens"],
                    estimated_cost_usd=r["estimated_cost_usd"],
                )
                for r in self._records
            ]
            db.add_all(logs)
            db.commit()
            count = len(logs)
            logger.info(f"CostTracker flushed {count} usage records for campaign {self.campaign_id}")
            self._records.clear()
            return count
        except Exception as e:
            logger.error(f"CostTracker.flush failed (non-fatal): {e}", exc_info=True)
            try:
                db.rollback()
            except Exception:
                pass
            return 0

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def total_cost(self) -> float:
        return sum(r["estimated_cost_usd"] for r in self._records)


def save_single_usage(
    db: Session,
    campaign_id: str,
    agent_name: str,
    call_type: str,
    response,
) -> None:
    """
    Save a single API usage record directly to the database.
    Used for standalone calls (e.g. article generation) that run
    outside the main campaign orchestration.
    """
    try:
        usage = response.usage
        model = response.model
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cost = calculate_cost(model, input_tokens, output_tokens)

        log = ApiUsageLog(
            campaign_id=uuid.UUID(campaign_id),
            agent_name=agent_name,
            call_type=call_type,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.warning(f"save_single_usage failed (non-fatal): {e}")
        try:
            db.rollback()
        except Exception:
            pass
