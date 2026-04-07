"""Escalation service — live agent hand-off logic."""

from __future__ import annotations

import uuid
from datetime import datetime

from app.models.schemas import SupportTicket

HIGH_RISK_TOPICS = {"appeal", "fraud", "overpayment", "identity theft", "identity_theft"}
ESCALATION_CONFIDENCE_THRESHOLD = 0.65
PENDING_DAYS_THRESHOLD = 21


def should_escalate(
    confidence: float,
    topic: str,
    claim_type: str | None = None,
    pending_days: int | None = None,
) -> bool:
    """Determine if the conversation should escalate to a live agent.

    Escalate when:
    - Model confidence is below threshold (< 0.65)
    - Topic involves a high-risk area (appeal, fraud, overpayment, identity theft)
    - Claim has been pending longer than 21 days
    """
    if confidence < ESCALATION_CONFIDENCE_THRESHOLD:
        return True

    normalized_topic = topic.lower().replace("-", " ").replace("_", " ")
    if normalized_topic in HIGH_RISK_TOPICS:
        return True

    if pending_days is not None and pending_days > PENDING_DAYS_THRESHOLD:
        return True

    return False


def _priority_for_reason(reason: str) -> str:
    """Derive ticket priority from the escalation reason."""
    lower = reason.lower()
    if any(term in lower for term in ("fraud", "identity theft")):
        return "urgent"
    if any(term in lower for term in ("appeal", "overpayment", "denied")):
        return "high"
    return "medium"


def _estimated_wait(priority: str) -> str:
    return {
        "urgent": "5-10 minutes",
        "high": "10-20 minutes",
        "medium": "20-40 minutes",
    }.get(priority, "20-40 minutes")


def create_support_ticket(
    reason: str,
    priority: str | None = None,
    claim_type: str | None = None,
    context: dict | None = None,
) -> SupportTicket:
    """Create a support ticket with full context for live agent hand-off."""
    if priority is None:
        priority = _priority_for_reason(reason)
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    return SupportTicket(
        ticket_id=ticket_id,
        reason=reason,
        priority=priority,
        claim_type=claim_type,
    )
