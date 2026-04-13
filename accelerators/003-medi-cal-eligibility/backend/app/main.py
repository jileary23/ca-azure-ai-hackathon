"""Medi-Cal Eligibility Agent — FastAPI application."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline import MediCalPipeline
from app.models.schemas import (
    ChatRequest, ChatResponse, ApplicationInfo,
    EligibilityScreenRequest, EligibilityScreenResponse,
    DocumentAnalyzeRequest, DocumentAnalyzeResponse,
    CompletenessRequest, CompletenessResponse,
    MediCalProgram,
)
from app.services.mock_service import MockMediCalService
from app.services.magi_engine import (
    screen_eligibility as magi_screen,
    calculate_magi,
    MEDI_CAL_THRESHOLDS,
)
from app.services.document_service import analyze_document, check_document_completeness
from app.services.fpl_service import get_fpl_guidelines as _get_fpl_guidelines

app = FastAPI(
    title="Medi-Cal Eligibility Agent API",
    description="AI-powered eligibility determination for DHCS Medi-Cal programs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = MediCalPipeline()
mock_service = MockMediCalService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "medi-cal-eligibility",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the 3-agent pipeline."""
    return await pipeline.process(request)


@app.get("/api/status")
async def status():
    """Return service status and configuration."""
    return {
        "service": "medi-cal-eligibility",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "agents": ["query_agent", "router_agent", "action_agent"],
        "supported_programs": ["MAGI_Adult", "MAGI_Child", "Pregnancy", "ABD", "QMB", "SLMB"],
    }


class _LegacyEligibilityScreenRequest(BaseModel):
    monthly_income: float
    household_size: int = 1
    program_type: str | None = None


@app.post("/api/eligibility/screen", response_model=EligibilityScreenResponse)
async def screen_eligibility(request: EligibilityScreenRequest):
    """MAGI-based Medi-Cal eligibility screening."""
    annual_income = request.monthly_income * 12
    magi_income = calculate_magi(annual_income)

    result = magi_screen(
        household_size=request.household_size,
        annual_income=magi_income,
        age=request.age,
        pregnant=request.pregnant,
        disabled=request.disabled,
        foster_youth=request.foster_youth,
    )

    return EligibilityScreenResponse(
        eligible_categories=result["eligible_categories"],
        fpl_percentage=result["fpl_percentage"],
        magi_income=magi_income,
        household_fpl=result["household_fpl"],
        confidence=result["confidence"],
        next_steps=result["next_steps"],
    )


class CreateApplicationRequest(BaseModel):
    applicant_name: str
    household_size: int = 1
    monthly_income: float = 0.0
    county: str = "Unknown"
    program_type: str = "MAGI_Adult"


@app.post("/api/applications")
async def create_application(request: CreateApplicationRequest):
    """Create a new Medi-Cal application."""
    app_data = request.model_dump()
    application = mock_service.create_application(app_data)
    return application


@app.get("/api/applications/{app_id}")
async def get_application(app_id: str):
    """Get application details by ID."""
    status = mock_service.get_application_status(app_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    return status


# ── New domain endpoints ──────────────────────────────────────────────

@app.post("/api/documents/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_doc(request: DocumentAnalyzeRequest):
    """Mock Document Intelligence OCR extraction."""
    result = analyze_document(request.document_type, request.content)
    return DocumentAnalyzeResponse(**result)


@app.post("/api/documents/completeness", response_model=CompletenessResponse)
async def check_completeness(request: CompletenessRequest):
    """Check document submission completeness."""
    result = check_document_completeness(
        submitted_docs=request.submitted_documents,
        application_type=request.application_type,
    )
    return CompletenessResponse(**result)


@app.get("/api/eligibility/fpl-guidelines")
async def get_fpl_guidelines():
    """Get current FPL thresholds for all Medi-Cal categories."""
    return _get_fpl_guidelines()


MEDI_CAL_PROGRAMS: list[dict] = [
    {
        "name": "Medi-Cal for Children",
        "description": "Health coverage for children under 19 with family income up to 266% FPL.",
        "category": "children_6_18",
        "fpl_threshold": 266,
        "age_range": "0–18",
        "special_requirements": [],
    },
    {
        "name": "MAGI Medi-Cal (Adults)",
        "description": "Coverage for adults 19–64 with income up to 138% FPL under ACA expansion.",
        "category": "adults_19_64",
        "fpl_threshold": 138,
        "age_range": "19–64",
        "special_requirements": [],
    },
    {
        "name": "Medi-Cal for Pregnant Individuals",
        "description": "Prenatal, delivery, and 12-month postpartum coverage up to 213% FPL.",
        "category": "pregnant",
        "fpl_threshold": 213,
        "age_range": "All ages",
        "special_requirements": ["Proof of pregnancy"],
    },
    {
        "name": "Aged & Disabled Medi-Cal",
        "description": "Coverage for individuals 65+ or with qualifying disabilities, up to 138% FPL.",
        "category": "aged_65_plus",
        "fpl_threshold": 138,
        "age_range": "65+",
        "special_requirements": ["Disability certification or age verification"],
    },
    {
        "name": "Disabled Medi-Cal",
        "description": "Coverage for individuals with qualifying disabilities, up to 138% FPL.",
        "category": "disabled",
        "fpl_threshold": 138,
        "age_range": "All ages",
        "special_requirements": ["Disability certification"],
    },
    {
        "name": "Former Foster Youth",
        "description": "Coverage for former foster youth under 26, up to 266% FPL.",
        "category": "former_foster_youth",
        "fpl_threshold": 266,
        "age_range": "Under 26",
        "special_requirements": ["Foster care documentation"],
    },
    {
        "name": "Parent/Caretaker Medi-Cal",
        "description": "Coverage for parent or caretaker relatives of dependent children, up to 138% FPL.",
        "category": "parents_caretakers",
        "fpl_threshold": 138,
        "age_range": "19–64",
        "special_requirements": ["Dependent child in household"],
    },
]


@app.get("/api/programs", response_model=list[MediCalProgram])
async def list_programs():
    """List Medi-Cal program variants."""
    return [MediCalProgram(**p) for p in MEDI_CAL_PROGRAMS]
