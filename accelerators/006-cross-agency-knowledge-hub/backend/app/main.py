"""Cross-Agency Knowledge Hub — FastAPI application."""

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, DocumentResult
from app.pipeline import KnowledgeHubPipeline
from app.services.mock_service import MockKnowledgeService
from app.services import (
    cross_reference_service,
    expert_service,
    permission_service,
    search_service,
)

settings = get_settings()

app = FastAPI(
    title="Cross-Agency Knowledge Hub API",
    description="Federated search across California state government knowledge bases",
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

pipeline = KnowledgeHubPipeline()
mock_service = MockKnowledgeService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "cross-agency-knowledge-hub",
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
        "max_results_per_agency": settings.max_results_per_agency,
        "cross_references_enabled": settings.enable_cross_references,
    }


@app.get("/api/search")
async def search(
    query: str = Query("", description="Search query"),
    agency: str | None = Query(None, description="Filter by agency code"),
    doc_type: str | None = Query(None, description="Filter by document type"),
    role: str = Query("public", description="User role for permission filtering"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
):
    """Federated search with agency-scoped permission filtering."""
    agencies = [agency] if agency else None
    doc_types = [doc_type] if doc_type else None
    permitted = permission_service.get_accessible_agencies(role)

    results = search_service.search(
        query=query or "search",
        agencies=agencies,
        doc_types=doc_types,
        limit=limit,
        user_permissions=permitted if role != "admin" else None,
    )
    return {
        "results": [d.model_dump() for d in results],
        "total": len(results),
        "role": role,
        "accessible_agencies": permitted,
    }


@app.get("/api/documents/{doc_id}")
async def get_document(
    doc_id: str,
    include_refs: bool = Query(True, description="Include cross-references"),
):
    """Get document detail with optional cross-references."""
    detail = search_service.get_document_detail(doc_id)
    if detail is None:
        return JSONResponse(status_code=404, content={"error": "Document not found"})
    if not include_refs:
        detail.pop("cross_references", None)
    return detail


@app.get("/api/experts")
async def find_experts(
    topic: str = Query(..., description="Topic to search experts for"),
    agency: str | None = Query(None, description="Filter by agency code"),
):
    """Find subject matter experts by topic."""
    experts = expert_service.find_experts(topic=topic, agency=agency)
    return {
        "experts": [e.model_dump() for e in experts],
        "total": len(experts),
    }


@app.get("/api/experts/{expert_id}")
async def get_expert(expert_id: str):
    """Get expert details."""
    expert = expert_service.get_expert(expert_id)
    if expert is None:
        return JSONResponse(status_code=404, content={"error": "Expert not found"})
    return expert.model_dump()


@app.get("/api/agencies")
async def list_agencies(
    role: str = Query("public", description="User role for permission filtering"),
):
    """List searchable agencies based on permission level."""
    info = permission_service.get_agency_info(role)
    return {
        "agencies": info,
        "total": len(info),
        "role": role,
    }


@app.get("/api/cross-references/{doc_id}")
async def get_cross_references(doc_id: str):
    """Get cross-references for a document."""
    refs = cross_reference_service.find_cross_references(doc_id)
    return {
        "doc_id": doc_id,
        "cross_references": [r.model_dump() for r in refs],
        "total": len(refs),
    }
