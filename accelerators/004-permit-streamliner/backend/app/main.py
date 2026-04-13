"""Permit Streamliner — FastAPI application."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClassifyRequest,
    ClassifyResponse,
    CreateApplicationRequest,
    FeeEstimateRequest,
    PermitApplication,
    ZoningResult,
)
from app.pipeline import PermitPipeline
from app.services.mock_service import MockPermitService
from app.services import intake_service, checklist_service, sla_service, fee_service

settings = get_settings()

app = FastAPI(
    title="Permit Streamliner API",
    description="AI-powered permit intake and routing for OPR, HCD, and DCA",
    version="0.1.0",
)

cors_origins_str = os.getenv("CORS_ORIGINS", "*")
if cors_origins_str == "*":
    _allow_origins = ["*"]
else:
    _allow_origins = [o.strip() for o in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = PermitPipeline()
mock_service = MockPermitService()

# In-memory store for created applications (mock mode)
_applications: dict[str, PermitApplication] = {}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "permit-streamliner",
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
        "supported_permit_types": settings.supported_permit_types.split(","),
        "max_review_days": settings.max_review_days,
    }


@app.get("/api/applications")
async def list_applications():
    return mock_service.get_sample_applications()


@app.get("/api/zoning/check")
async def zoning_check(address: str = "123 Main St") -> dict:
    return mock_service.get_zoning_info(address)


# --- Domain endpoints ---


@app.post("/api/intake/classify", response_model=ClassifyResponse)
async def classify_project(request: ClassifyRequest) -> ClassifyResponse:
    """Classify project type and determine responsible agency."""
    result = intake_service.classify_project(request.description)
    return ClassifyResponse(**result)


@app.post("/api/applications/create", response_model=PermitApplication)
async def create_application(request: CreateApplicationRequest) -> PermitApplication:
    """Create a new permit application."""
    application = intake_service.create_application(
        project_type=request.project_type,
        description=request.project_description,
        address=request.address,
        applicant=request.applicant_name,
        project_value=request.project_value,
    )
    _applications[application.app_id] = application
    return application


@app.get("/api/applications/{app_id}/checklist")
async def get_application_checklist(app_id: str):
    """Get document checklist for an application."""
    application = _applications.get(app_id)
    if not application:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    cl = checklist_service.generate_checklist(application.project_type)
    return cl


@app.get("/api/applications/{app_id}/status")
async def get_application_status(app_id: str):
    """Get application status with SLA tracking."""
    application = _applications.get(app_id)
    if not application:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    return sla_service.get_sla_status(application)


@app.post("/api/fees/estimate")
async def estimate_fees(request: FeeEstimateRequest):
    """Estimate permit fees for a project."""
    return fee_service.estimate_fees(
        project_type=request.project_type,
        project_value=request.project_value,
        expedited=request.expedited,
        constraints=request.constraints,
    )
