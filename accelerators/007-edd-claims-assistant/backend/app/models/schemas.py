"""Pydantic v2 models for EDD Claims Assistant."""

from datetime import datetime
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    text: str
    policy_ref: str | None = None


class ClaimQuery(BaseModel):
    raw_input: str
    intent: str
    claim_type: str | None = None  # UI/DI/PFL
    entities: dict = Field(default_factory=dict)


class ClaimStatus(BaseModel):
    claim_id: str
    claim_type: str
    status: str  # active/pending/denied/exhausted/on_hold
    filed_date: datetime
    last_certified: datetime | None = None
    weekly_benefit_amount: float
    remaining_balance: float
    pending_issues: list[str] = Field(default_factory=list)
    next_payment_date: datetime | None = None


class EligibilityAssessment(BaseModel):
    claim_type: str
    likely_eligible: bool
    confidence: float
    factors: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class DocumentItem(BaseModel):
    name: str
    required: bool
    submitted: bool
    description: str


class IdentityVerification(BaseModel):
    last_four_ssn: str
    date_of_birth: str
    verified: bool


class PolicyArticle(BaseModel):
    article_id: str
    title: str
    content: str
    claim_types: list[str] = Field(default_factory=list)
    last_updated: datetime


class SupportTicket(BaseModel):
    ticket_id: str
    reason: str
    priority: str
    claim_type: str | None = None


class BenefitCalculationRequest(BaseModel):
    claim_type: str  # UI, DI, PFL
    quarterly_earnings: list[float]


class BenefitCalculationResponse(BaseModel):
    claim_type: str
    weekly_benefit: float
    max_weeks: int
    total_benefit: float
    replacement_rate: float
    base_period_earnings: float


class ClaimTimeline(BaseModel):
    claim_type: str
    estimated_days: int
    steps: list[dict] = Field(default_factory=list)


class ClaimRequirements(BaseModel):
    claim_type: str
    eligibility_requirements: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    additional_info: list[str] = Field(default_factory=list)


class EscalationRequest(BaseModel):
    reason: str
    claim_type: str | None = None
    context: dict = Field(default_factory=dict)


class EscalationResponse(BaseModel):
    ticket_id: str
    priority: str
    estimated_wait: str
    queue_position: int


class ClaimStatusRequest(BaseModel):
    claim_type: str = "UI"
    last_four_ssn: str = ""
    date_of_birth: str = ""


class EligibilityRequest(BaseModel):
    claim_type: str = "UI"


class DocumentChecklistRequest(BaseModel):
    claim_type: str = "UI"


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    claim_status: ClaimStatus | None = None
    eligibility: EligibilityAssessment | None = None
    document_checklist: list[DocumentItem] | None = None


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


class RoutingDecision(BaseModel):
    department: str
    priority: str
    reason: str
    escalate: bool = False
