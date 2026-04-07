"""BenefitsCal Navigator — FastAPI application."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    CountyOffice,
    PrescreenRequest,
    PrescreenResponse,
    PrescreenResult,
    ProgramInfo,
)
from app.pipeline import BenefitsCalPipeline
from app.services import county_service, language_service
from app.services.fpl_service import (
    calculate_fpl,
    calculate_fpl_percentage,
    prescreen_eligibility as fpl_prescreen,
)
from app.services.mock_service import MockBenefitsService

settings = get_settings()

app = FastAPI(
    title="BenefitsCal Navigator API",
    description="AI-powered benefits eligibility assistant for CDSS programs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = BenefitsCalPipeline()
mock_service = MockBenefitsService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "benefitscal-navigator",
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
        "supported_languages": settings.supported_languages.split(","),
    }


@app.get("/api/programs", response_model=list[ProgramInfo])
async def list_programs() -> list[ProgramInfo]:
    programs = mock_service.list_programs()
    return [
        ProgramInfo(
            program_id=p["program_id"],
            name=p["name"],
            description=p["description"],
            agency=p["agency"],
            requirements=p["requirements"],
            documents_needed=p["documents_needed"],
        )
        for p in programs
    ]


# ---------------------------------------------------------------------------
# Domain endpoints
# ---------------------------------------------------------------------------


@app.post("/api/eligibility/prescreen", response_model=PrescreenResponse)
async def prescreen_eligibility(request: PrescreenRequest) -> PrescreenResponse:
    """FPL-based pre-screening for benefits programs."""
    if request.household_size < 1:
        raise HTTPException(status_code=422, detail="household_size must be >= 1")
    if request.monthly_income < 0:
        raise HTTPException(status_code=422, detail="monthly_income must be >= 0")

    annual_income = request.monthly_income * 12
    fpl_amount = calculate_fpl(request.household_size)
    fpl_pct = calculate_fpl_percentage(request.household_size, annual_income)

    raw_results = fpl_prescreen(
        household_size=request.household_size,
        monthly_income=request.monthly_income,
        programs=request.programs,
    )

    results = [PrescreenResult(**r) for r in raw_results]

    return PrescreenResponse(
        household_size=request.household_size,
        monthly_income=request.monthly_income,
        annual_income=annual_income,
        fpl_amount=fpl_amount,
        fpl_percentage=round(fpl_pct, 1),
        results=results,
    )


@app.get("/api/programs/{program_id}/requirements")
async def get_program_requirements(program_id: str):
    """Get detailed requirements for a specific program."""
    program = mock_service.get_program(program_id)
    if program is None:
        raise HTTPException(status_code=404, detail=f"Program '{program_id}' not found")
    return {
        "program_id": program["program_id"],
        "name": program["name"],
        "description": program["description"],
        "agency": program["agency"],
        "requirements": program["requirements"],
        "documents_needed": program["documents_needed"],
        "income_limits": program.get("income_limits", {}),
        "policy_ref": program.get("policy_ref"),
    }


@app.get("/api/offices", response_model=list[CountyOffice])
async def get_county_offices(
    county: str | None = Query(None, description="Filter by county name"),
) -> list[CountyOffice]:
    """Find county welfare offices, optionally filtered by county."""
    return county_service.get_offices(county)


@app.get("/api/languages")
async def get_supported_languages():
    """List supported languages."""
    return language_service.get_supported_languages()
