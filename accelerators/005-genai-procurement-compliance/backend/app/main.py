"""GenAI Procurement Compliance — FastAPI application."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    AttestationRequest,
    ChatRequest,
    ChatResponse,
    ComplianceReport,
    ComplianceScoreDetail,
    NistClassification,
)
from app.pipeline import process_message
from app.services.mock_service import MockComplianceService
from app.services.nist_mapper import classify_system
from app.services.rule_engine import get_rules, match_rules
from app.services.scoring_engine import score_attestation

app = FastAPI(
    title="GenAI Procurement Compliance API",
    description="Automated vendor attestation review and compliance scoring for CDT/DGS",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_service = MockComplianceService()

# In-memory store for attestation reports (mock mode)
_report_store: dict[str, ComplianceReport] = {}
_report_counter = 0


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "genai-procurement-compliance",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await process_message(request)


@app.get("/api/status")
async def status():
    return {
        "service": "genai-procurement-compliance",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "compliance_frameworks": ["EO_N-5-26", "SB_53", "NIST_AI_RMF"],
        "endpoints": ["/health", "/api/chat", "/api/status", "/api/attestations"],
    }


@app.post("/api/attestations")
async def upload_attestation():
    doc = mock_service.create_attestation()
    return {"attestation": doc.model_dump(mode="json")}


@app.get("/api/attestations/{doc_id}/results")
async def get_attestation_results(doc_id: str):
    results = mock_service.get_compliance_results()
    score = mock_service.get_compliance_score()
    return {
        "doc_id": doc_id,
        "score": score.model_dump(),
        "results": [r.model_dump() for r in results],
    }


# ---- New domain-specific endpoints ----


@app.post("/api/attestations/analyze", response_model=ComplianceScoreDetail)
async def analyze_attestation(request: AttestationRequest):
    """Analyze vendor attestation document for compliance."""
    global _report_counter
    score = score_attestation(request.text)

    # Store a report for later retrieval
    _report_counter += 1
    att_id = f"ATT-{_report_counter:04d}"
    rule_matches = match_rules(request.text)
    nist_class = classify_system(request.system_description)
    report = ComplianceReport(
        attestation_id=att_id,
        vendor_name=request.vendor_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        score=score,
        rule_matches=rule_matches,
        nist_classification=nist_class,
    )
    _report_store[att_id] = report

    return score


@app.get("/api/compliance/rules")
async def get_compliance_rules(source: str = Query(None)):
    """List all compliance rules, optionally filtered by source."""
    rules = get_rules(source)
    return {"rules": [r.model_dump() for r in rules], "count": len(rules)}


@app.get("/api/compliance/report/{attestation_id}", response_model=ComplianceReport)
async def get_compliance_report(attestation_id: str):
    """Get detailed compliance report for a previous attestation analysis."""
    if attestation_id in _report_store:
        return _report_store[attestation_id]

    # Return a pre-generated sample report for any unknown ID
    sample_score = score_attestation(
        "Our AI system implements content safety filters, bias testing with demographic parity, "
        "transparency disclosure, data privacy protections compliant with CCPA, and human oversight "
        "with escalation procedures. We conduct risk assessments and maintain audit trails."
    )
    sample_rules = match_rules(
        "content safety bias testing transparency data privacy human oversight risk assessment audit trail"
    )
    sample_nist = classify_system("AI governance system with testing and monitoring capabilities")
    return ComplianceReport(
        attestation_id=attestation_id,
        vendor_name="Sample Vendor",
        timestamp=datetime.now(timezone.utc).isoformat(),
        score=sample_score,
        rule_matches=sample_rules,
        nist_classification=sample_nist,
    )


@app.get("/api/nist/classify", response_model=NistClassification)
async def classify_nist(description: str = Query(...)):
    """Classify an AI system against NIST AI RMF."""
    return classify_system(description)
