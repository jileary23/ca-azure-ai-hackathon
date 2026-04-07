"""Pydantic v2 models for Permit Streamliner."""

from datetime import datetime
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    text: str
    policy_ref: str | None = None
    url: str | None = None


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


class PermitQuery(BaseModel):
    raw_input: str
    intent: str
    entities: dict = Field(default_factory=dict)
    project_type: str | None = None
    address: str | None = None


class PermitApplication(BaseModel):
    app_id: str
    applicant_name: str
    project_type: str
    project_description: str
    address: str
    status: str = "draft"  # draft/submitted/under_review/approved/denied/revision_needed
    submitted_at: datetime | None = None
    estimated_completion: datetime | None = None


class PermitRequirement(BaseModel):
    req_id: str
    name: str
    description: str
    category: str  # building/electrical/plumbing/zoning/fire/environmental/health
    required: bool = True
    document_type: str = ""


class ChecklistItem(BaseModel):
    name: str
    required: bool = True
    submitted: bool = False
    status: str = "pending"  # pending/approved/rejected


class DocumentChecklist(BaseModel):
    items: list[ChecklistItem] = Field(default_factory=list)


class ZoningResult(BaseModel):
    address: str
    zone_code: str
    zone_name: str
    permitted_uses: list[str] = Field(default_factory=list)
    conditional_uses: list[str] = Field(default_factory=list)
    setbacks: dict = Field(default_factory=dict)
    max_height_ft: float = 35.0
    lot_coverage_pct: float = 50.0
    compliant: bool = True
    issues: list[str] = Field(default_factory=list)


class RoutingDecision(BaseModel):
    departments: list[str] = Field(default_factory=list)
    priority: str = "medium"  # low/medium/high/critical
    reason: str = ""
    escalate: bool = False
    sla_days: int = 30


class SLAStatus(BaseModel):
    application_id: str
    department: str
    assigned_date: datetime
    due_date: datetime
    status: str = "on_track"  # on_track/at_risk/breached
    days_remaining: int = 30


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


# --- Domain endpoint models ---


class ClassifyRequest(BaseModel):
    description: str
    address: str | None = None


class ClassifyResponse(BaseModel):
    project_type: str
    agency: str
    estimated_sla_days: int
    estimated_fees: float
    confidence: float


class CreateApplicationRequest(BaseModel):
    applicant_name: str
    project_type: str
    project_description: str
    address: str
    project_value: float = 0


class FeeEstimateRequest(BaseModel):
    project_type: str
    project_value: float = 0
    expedited: bool = False
    constraints: list[str] = Field(default_factory=list)


class FeeEstimate(BaseModel):
    base_fee: float
    modifiers: list[dict] = Field(default_factory=list)
    total_fee: float
    breakdown: dict = Field(default_factory=dict)
