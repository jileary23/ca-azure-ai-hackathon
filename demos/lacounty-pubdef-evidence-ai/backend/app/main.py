"""LA County Public Defender — Evidence AI FastAPI application."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    CaseSummary,
    EvidenceQueryRequest,
    EvidenceQueryResponse,
    VideoSubmitRequest,
    VideoSubmitResponse,
)
from app.services import mock_service
from app.pipeline import get_job, process_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="LA County Public Defender — Evidence AI",
    description=(
        "Analyzes body cam footage using Azure Video Indexer and GPT-4o "
        "to assist Public Defender attorneys with evidence review."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "mock_mode": settings.use_mock_services,
    }


# ---------------------------------------------------------------------------
# Video submission
# ---------------------------------------------------------------------------


@app.post("/api/analyze", response_model=VideoSubmitResponse)
async def submit_analysis(request: VideoSubmitRequest) -> VideoSubmitResponse:
    """
    Submit a body cam video URL for analysis.

    In mock mode, returns a fully pre-processed result immediately.
    In production mode, submits to Azure Video Indexer and queues GPT-4o analysis.
    """
    use_mock = request.use_mock or settings.use_mock_services

    if use_mock:
        result = mock_service.create_mock_job(
            case_number=request.case_number,
            incident_date=request.incident_date,
        )
        return VideoSubmitResponse(
            job_id=result.job_id,
            status=AnalysisStatus.COMPLETED,
            case_number=request.case_number,
            message="Mock analysis complete. Full results available immediately.",
            estimated_duration_seconds=0,
        )

    # Production path — requires Azure credentials in .env
    if not request.video_url:
        raise HTTPException(
            status_code=400, detail="video_url is required in production mode."
        )
    if not settings.video_indexer_account_id:
        raise HTTPException(
            status_code=503,
            detail="Azure Video Indexer not configured. Set VIDEO_INDEXER_* environment variables.",
        )

    result = await process_video(request)
    return VideoSubmitResponse(
        job_id=result.job_id,
        status=result.status,
        case_number=result.case_number,
        message="Video submitted to Azure Video Indexer. Analysis in progress.",
        estimated_duration_seconds=int((result.video_duration_seconds or 600) * 0.5),
    )


# ---------------------------------------------------------------------------
# Analysis retrieval
# ---------------------------------------------------------------------------


@app.get("/api/analysis/{job_id}", response_model=AnalysisResult)
async def get_analysis(job_id: str) -> AnalysisResult:
    """Return the full analysis result for a submitted video."""
    # Check mock store first, then production store
    result = mock_service.get_mock_job(job_id) or get_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return result


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------


@app.post("/api/query", response_model=EvidenceQueryResponse)
async def query_evidence(request: EvidenceQueryRequest) -> EvidenceQueryResponse:
    """
    Ask a natural-language question about analyzed evidence.

    Example questions:
    - "Were Miranda rights read before questioning?"
    - "Did the officer identify a reason for the stop?"
    - "What happened at the 3-minute mark?"
    """
    result = mock_service.get_mock_job(request.job_id) or get_job(request.job_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Job '{request.job_id}' not found."
        )
    if result.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Analysis not yet complete.")

    if settings.use_mock_services or result.video_indexer_video_id.startswith("mock-"):
        return mock_service.mock_query(request.job_id, request.question)

    from app.services.evidence_analyzer import query_evidence as gpt_query

    return await gpt_query(
        transcript=result.transcript,
        key_moments=result.key_moments,
        question=request.question,
    )


# ---------------------------------------------------------------------------
# Case list
# ---------------------------------------------------------------------------


@app.get("/api/cases", response_model=list[CaseSummary])
async def list_cases() -> list[CaseSummary]:
    """Return all analyzed cases (mock store only in demo mode)."""
    return mock_service.list_mock_cases()
