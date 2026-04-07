"""Schema model tests."""

from datetime import datetime
from app.models.schemas import (
    BenefitCalculationRequest,
    BenefitCalculationResponse,
    ChatRequest,
    ChatResponse,
    Citation,
    ClaimQuery,
    ClaimRequirements,
    ClaimStatus,
    ClaimStatusRequest,
    ClaimTimeline,
    DocumentChecklistRequest,
    DocumentItem,
    EligibilityAssessment,
    EligibilityRequest,
    EscalationRequest,
    EscalationResponse,
    IdentityVerification,
    PolicyArticle,
    SupportTicket,
    AgentResponse,
    RoutingDecision,
)


def test_chat_request_defaults():
    req = ChatRequest(message="test")
    assert req.language == "en"
    assert req.session_id is None


def test_chat_response():
    resp = ChatResponse(
        response="Test response",
        confidence=0.9,
        citations=[Citation(source="EDD", text="test")],
    )
    assert resp.confidence == 0.9
    assert resp.claim_status is None
    assert resp.eligibility is None
    assert resp.document_checklist is None


def test_citation():
    c = Citation(source="EDD Policy", text="Section 1", policy_ref="CUIC §1253")
    assert c.policy_ref == "CUIC §1253"


def test_claim_query():
    q = ClaimQuery(
        raw_input="test",
        intent="claim_status",
        claim_type="UI",
    )
    assert q.claim_type == "UI"
    assert q.entities == {}


def test_claim_status():
    cs = ClaimStatus(
        claim_id="UI-001",
        claim_type="UI",
        status="active",
        filed_date=datetime(2025, 1, 1),
        weekly_benefit_amount=450.0,
        remaining_balance=9000.0,
    )
    assert cs.status == "active"
    assert cs.pending_issues == []


def test_eligibility_assessment():
    ea = EligibilityAssessment(
        claim_type="UI",
        likely_eligible=True,
        confidence=0.85,
        factors=["Factor 1"],
        requirements=["Req 1"],
        next_steps=["Step 1"],
    )
    assert ea.likely_eligible is True


def test_document_item():
    di = DocumentItem(
        name="Photo ID",
        required=True,
        submitted=False,
        description="Government-issued ID",
    )
    assert di.required is True
    assert di.submitted is False


def test_identity_verification():
    iv = IdentityVerification(
        last_four_ssn="1234",
        date_of_birth="01/15/1990",
        verified=True,
    )
    assert iv.verified is True


def test_policy_article():
    pa = PolicyArticle(
        article_id="POL-001",
        title="Test Policy",
        content="Content",
        claim_types=["UI", "DI"],
        last_updated=datetime(2024, 1, 1),
    )
    assert "UI" in pa.claim_types


def test_support_ticket():
    st = SupportTicket(
        ticket_id="TKT-001",
        reason="Claim denied",
        priority="high",
        claim_type="UI",
    )
    assert st.priority == "high"


def test_agent_response():
    r = AgentResponse(
        intent="claim_status",
        response_text="Your claim is active",
        confidence=0.9,
    )
    assert r.data is None


def test_routing_decision():
    d = RoutingDecision(
        department="claims_services",
        priority="medium",
        reason="Test",
        escalate=False,
    )
    assert d.escalate is False


def test_benefit_calculation_request():
    req = BenefitCalculationRequest(claim_type="UI", quarterly_earnings=[5000.0, 4000.0])
    assert req.claim_type == "UI"
    assert len(req.quarterly_earnings) == 2


def test_benefit_calculation_response():
    resp = BenefitCalculationResponse(
        claim_type="UI",
        weekly_benefit=450.0,
        max_weeks=26,
        total_benefit=11700.0,
        replacement_rate=1.0,
        base_period_earnings=20000.0,
    )
    assert resp.total_benefit == 11700.0


def test_claim_timeline():
    ct = ClaimTimeline(
        claim_type="UI",
        estimated_days=21,
        steps=[{"step": 1, "name": "Filed"}],
    )
    assert ct.estimated_days == 21
    assert len(ct.steps) == 1


def test_claim_requirements():
    cr = ClaimRequirements(
        claim_type="UI",
        eligibility_requirements=["Req 1"],
        required_documents=["Doc 1"],
        additional_info=["Info 1"],
    )
    assert cr.claim_type == "UI"
    assert len(cr.eligibility_requirements) == 1


def test_escalation_request_defaults():
    req = EscalationRequest(reason="Need help")
    assert req.claim_type is None
    assert req.context == {}


def test_escalation_response():
    resp = EscalationResponse(
        ticket_id="TKT-001",
        priority="high",
        estimated_wait="10-20 minutes",
        queue_position=3,
    )
    assert resp.queue_position == 3


def test_claim_status_request_defaults():
    req = ClaimStatusRequest()
    assert req.claim_type == "UI"
    assert req.last_four_ssn == ""


def test_eligibility_request_defaults():
    req = EligibilityRequest()
    assert req.claim_type == "UI"


def test_document_checklist_request_defaults():
    req = DocumentChecklistRequest()
    assert req.claim_type == "UI"
