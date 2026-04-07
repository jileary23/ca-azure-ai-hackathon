"""Pydantic v2 models for GenAI Procurement Compliance."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    document_id: str | None = None


class Citation(BaseModel):
    source: str
    text: str
    regulation: str | None = None


class ComplianceQuery(BaseModel):
    raw_input: str
    intent: str = "compliance_check"
    entities: dict = Field(default_factory=dict)


class AttestationDocument(BaseModel):
    doc_id: str
    vendor_name: str
    upload_date: datetime | None = None
    file_type: str = "pdf"
    status: Literal["pending", "analyzing", "complete", "error"] = "pending"


class ComplianceRule(BaseModel):
    rule_id: str
    category: str
    requirement: str
    regulation_source: Literal["EO_N-5-26", "SB_53", "NIST_AI_RMF"]
    severity: Literal["critical", "high", "medium", "low"]


class ComplianceResult(BaseModel):
    rule_id: str
    status: Literal["compliant", "non_compliant", "partial", "not_assessed"]
    evidence: str
    confidence: float = 0.0
    findings: str = ""


class ComplianceScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    category_scores: dict[str, float] = Field(default_factory=dict)
    risk_classification: Literal["low", "medium", "high", "critical"] = "medium"
    compliant_count: int = 0
    non_compliant_count: int = 0
    partial_count: int = 0


class ComplianceGap(BaseModel):
    rule_id: str
    category: str
    requirement: str
    severity: Literal["critical", "high", "medium", "low"]
    remediation_guidance: str
    estimated_effort: Literal["low", "medium", "high"]


class GapAnalysis(BaseModel):
    gaps: list[ComplianceGap] = Field(default_factory=list)


class RiskClassification(BaseModel):
    tier: int = Field(ge=1, le=4)
    classification: str
    justification: str


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None


class RoutingDecision(BaseModel):
    department: str
    priority: Literal["low", "medium", "high", "critical"]
    reason: str
    escalate: bool = False


class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    compliance_data: dict | None = None


# ---- Domain-specific models for new endpoints ----


class AttestationRequest(BaseModel):
    text: str
    vendor_name: str
    system_description: str


class ComplianceScoreDetail(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    risk_tier: Literal["low", "medium", "high", "critical"]
    category_scores: dict[str, float] = Field(default_factory=dict)
    gaps: list[dict[str, str]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ComplianceRuleDetail(BaseModel):
    id: str
    category: str
    requirement: str
    source: str
    severity: Literal["critical", "high", "medium", "low"]
    keywords: list[str] = Field(default_factory=list)


class RuleMatch(BaseModel):
    rule_id: str
    category: str
    matched_keywords: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class NistControl(BaseModel):
    control_id: str
    function: str
    title: str
    description: str


class NistClassification(BaseModel):
    risk_tier: Literal["low", "medium", "high"]
    applicable_functions: list[str] = Field(default_factory=list)
    controls: list[NistControl] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    attestation_id: str
    vendor_name: str
    timestamp: str
    score: ComplianceScoreDetail
    rule_matches: list[RuleMatch] = Field(default_factory=list)
    nist_classification: NistClassification | None = None
