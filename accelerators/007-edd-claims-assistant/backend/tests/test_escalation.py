"""Tests for escalation_service."""

from app.services.escalation_service import (
    should_escalate,
    create_support_ticket,
)


class TestShouldEscalate:
    def test_low_confidence_triggers(self):
        assert should_escalate(confidence=0.40, topic="general") is True

    def test_high_confidence_no_escalation(self):
        assert should_escalate(confidence=0.90, topic="general") is False

    def test_threshold_exact(self):
        # At threshold (0.65) should NOT escalate
        assert should_escalate(confidence=0.65, topic="general") is False

    def test_just_below_threshold(self):
        assert should_escalate(confidence=0.64, topic="general") is True

    def test_appeal_topic(self):
        assert should_escalate(confidence=0.90, topic="appeal") is True

    def test_fraud_topic(self):
        assert should_escalate(confidence=0.90, topic="fraud") is True

    def test_overpayment_topic(self):
        assert should_escalate(confidence=0.90, topic="overpayment") is True

    def test_identity_theft_topic(self):
        assert should_escalate(confidence=0.90, topic="identity theft") is True

    def test_identity_theft_underscore(self):
        assert should_escalate(confidence=0.90, topic="identity_theft") is True

    def test_pending_days_over_threshold(self):
        assert should_escalate(confidence=0.90, topic="general", pending_days=25) is True

    def test_pending_days_at_threshold(self):
        assert should_escalate(confidence=0.90, topic="general", pending_days=21) is False


class TestCreateSupportTicket:
    def test_creates_ticket(self):
        ticket = create_support_ticket(reason="Claim denied", claim_type="UI")
        assert ticket.ticket_id.startswith("TKT-")
        assert ticket.reason == "Claim denied"
        assert ticket.claim_type == "UI"

    def test_fraud_gets_urgent_priority(self):
        ticket = create_support_ticket(reason="Suspected fraud on my account")
        assert ticket.priority == "urgent"

    def test_appeal_gets_high_priority(self):
        ticket = create_support_ticket(reason="I need to appeal my denial")
        assert ticket.priority == "high"

    def test_general_gets_medium_priority(self):
        ticket = create_support_ticket(reason="I have a question about certification")
        assert ticket.priority == "medium"

    def test_custom_priority(self):
        ticket = create_support_ticket(reason="test", priority="low")
        assert ticket.priority == "low"
