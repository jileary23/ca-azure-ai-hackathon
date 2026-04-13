"""EDD Claims Assistant — FastAPI application."""

import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import (
    BenefitCalculationRequest,
    BenefitCalculationResponse,
    ChatRequest,
    ChatResponse,
    ClaimRequirements,
    ClaimStatusRequest,
    ClaimTimeline,
    DocumentChecklistRequest,
    EligibilityRequest,
    EscalationRequest,
    EscalationResponse,
)
from app.pipeline import EDDClaimsPipeline
from app.services.mock_service import MockEDDService
from app.services import benefit_calculator
from app.services import claim_service
from app.services import escalation_service

settings = get_settings()

app = FastAPI(
    title="EDD Claims Assistant API",
    description="AI-powered claims status and eligibility assistant for EDD",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = EDDClaimsPipeline()
mock_service = MockEDDService()

VALID_CLAIM_TYPES = {"ui", "di", "pfl"}

# ── Document requirements by claim type (for /api/claims/{type}/requirements) ──
CLAIM_REQUIREMENTS: dict[str, dict] = {
    "ui": {
        "claim_type": "UI",
        "eligibility_requirements": [
            "Earned at least $1,300 in highest quarter of base period",
            "Or earned at least $900 in highest quarter with total base period earnings >= 1.25× highest quarter",
            "Lost job through no fault of your own (layoff, reduction in force)",
            "Physically able to work and available for full-time employment",
            "Actively searching for work each week",
        ],
        "required_documents": [
            "Government-issued photo ID (driver's license, state ID, or passport)",
            "Social Security card or document showing SSN",
            "Last employer information (name, address, dates, separation reason)",
            "Wage records / pay stubs from the last 18 months",
        ],
        "additional_info": [
            "Base period is the first 4 of the last 5 completed calendar quarters",
            "You must register with CalJOBS within 21 days of filing",
            "Certify for benefits every two weeks",
            "If a veteran, provide DD-214 for military service in the last 18 months",
        ],
    },
    "di": {
        "claim_type": "DI",
        "eligibility_requirements": [
            "Currently covered by State Disability Insurance (SDI) through payroll deductions",
            "Earned at least $300 in base period from which SDI deductions were withheld",
            "Unable to perform regular or customary work for at least 8 consecutive days",
            "Under care and treatment of a licensed physician or practitioner",
            "Filed claim within 49 days of becoming disabled",
        ],
        "required_documents": [
            "Physician's Certificate (form DE 2525XX) completed by treating physician",
            "Government-issued photo ID",
            "Medical records (diagnosis, treatment plan, expected return-to-work date)",
            "Current employer name and contact information",
        ],
        "additional_info": [
            "There is a 7-day unpaid waiting period before benefits begin",
            "Benefits are approximately 60-70% of wages (up to $1,620/week in 2024)",
            "Maximum benefit duration is 52 weeks",
            "Work-related injuries are covered by Workers' Compensation, not DI",
        ],
    },
    "pfl": {
        "claim_type": "PFL",
        "eligibility_requirements": [
            "Contributed to SDI through payroll deductions in the past 12 months",
            "Earned at least $300 in base period",
            "Need time off for qualifying reason: bonding with new child, caring for seriously ill family member, or military assist",
        ],
        "required_documents": [
            "Government-issued photo ID",
            "Birth certificate or adoption papers (for bonding claims)",
            "Medical certification from physician (for care claims)",
            "Proof of employer notification of leave",
            "Military documentation (for military assist claims, if applicable)",
        ],
        "additional_info": [
            "Maximum benefit duration is 8 weeks",
            "Benefits are approximately 60-70% of wages (up to $1,620/week in 2024)",
            "Notify your employer at least 30 days in advance if leave is foreseeable",
            "PFL does not provide job protection — check CFRA/FMLA for that",
        ],
    },
}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "edd-claims-assistant",
        "mock_mode": settings.use_mock_services,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "mock_mode": settings.use_mock_services,
        "supported_claim_types": settings.supported_claim_types.split(","),
    }


@app.post("/api/claim-status")
async def claim_status(request: ClaimStatusRequest):
    if settings.identity_verification_required and request.last_four_ssn:
        mock_service.verify_identity(request.last_four_ssn, request.date_of_birth)
    claim = mock_service.get_claim(request.claim_type)
    if claim is None:
        return {"error": "Claim not found"}
    return claim.model_dump()


@app.post("/api/eligibility")
async def eligibility(request: EligibilityRequest):
    assessment = mock_service.get_eligibility(request.claim_type)
    return assessment.model_dump()


@app.post("/api/document-checklist")
async def document_checklist(request: DocumentChecklistRequest):
    checklist = mock_service.get_document_checklist(request.claim_type)
    return [item.model_dump() for item in checklist]


# ── New domain endpoints ─────────────────────────────────────────────────────


@app.post("/api/benefits/calculate", response_model=BenefitCalculationResponse)
async def calculate_benefits(request: BenefitCalculationRequest):
    """Calculate estimated benefit amounts for UI, DI, or PFL."""
    ct = request.claim_type.upper()
    calculators = {
        "UI": benefit_calculator.calculate_ui_benefit,
        "DI": benefit_calculator.calculate_di_benefit,
        "PFL": benefit_calculator.calculate_pfl_benefit,
    }
    calc_fn = calculators.get(ct)
    if calc_fn is None:
        raise HTTPException(status_code=400, detail=f"Unsupported claim type: {ct}")
    result = calc_fn(request.quarterly_earnings)
    return BenefitCalculationResponse(**result)


@app.get("/api/claims/{claim_type}/timeline", response_model=ClaimTimeline)
async def get_claim_timeline(claim_type: str):
    """Get expected processing timeline for a claim type."""
    timeline = claim_service.get_claim_timeline(claim_type)
    if timeline is None:
        raise HTTPException(
            status_code=404, detail=f"No timeline for claim type: {claim_type}"
        )
    return ClaimTimeline(**timeline)


@app.get("/api/claims/{claim_type}/requirements", response_model=ClaimRequirements)
async def get_claim_requirements(claim_type: str):
    """Get eligibility requirements and required documents for a claim type."""
    reqs = CLAIM_REQUIREMENTS.get(claim_type.lower())
    if reqs is None:
        raise HTTPException(
            status_code=404, detail=f"No requirements for claim type: {claim_type}"
        )
    return ClaimRequirements(**reqs)


@app.post("/api/escalate", response_model=EscalationResponse)
async def escalate_to_agent(request: EscalationRequest):
    """Escalate to live agent with context transfer."""
    ticket = escalation_service.create_support_ticket(
        reason=request.reason,
        claim_type=request.claim_type,
        context=request.context,
    )
    wait = escalation_service._estimated_wait(ticket.priority)
    queue_pos = random.randint(1, 8)
    return EscalationResponse(
        ticket_id=ticket.ticket_id,
        priority=ticket.priority,
        estimated_wait=wait,
        queue_position=queue_pos,
    )
