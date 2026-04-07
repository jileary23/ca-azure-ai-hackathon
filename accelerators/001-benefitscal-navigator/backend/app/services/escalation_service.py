"""Confidence-based escalation service for BenefitsCal Navigator."""

import uuid
from datetime import datetime, timezone

from app.models.schemas import EscalationTicket

CONFIDENCE_THRESHOLD = 0.7

HIGH_RISK_TOPICS: set[str] = {
    "appeal",
    "overpayment",
    "fraud",
    "disability",
    "emergency",
}


def should_escalate(confidence: float, topic: str) -> bool:
    """Return True if the query should be escalated to a human agent.

    Triggers:
    - Confidence score below 0.7
    - Topic is in the high-risk list
    """
    if confidence < CONFIDENCE_THRESHOLD:
        return True
    if topic.lower() in HIGH_RISK_TOPICS:
        return True
    return False


def create_escalation(
    reason: str,
    priority: str = "medium",
    context: dict | None = None,
) -> EscalationTicket:
    """Create an escalation ticket for human review."""
    ticket_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    return EscalationTicket(
        ticket_id=ticket_id,
        reason=reason,
        priority=priority,
        created_at=datetime.now(timezone.utc),
    )
