"""Wildfire Response Coordinator — FastAPI application."""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline import WildfirePipeline
from app.models.schemas import (
    ChatRequest, ChatResponse,
    CreateIncidentRequest, IncidentResponse,
    ResourceAllocationRequest, ResourceAllocationResponse,
    EvacuationRoute, WeatherAlert, FireWeather, PSPSStatus,
)
from app.services.mock_service import MockWildfireService
from app.services import incident_service, resource_service, weather_service, evacuation_service, psps_service

app = FastAPI(
    title="Wildfire Response Coordinator API",
    description="AI-powered emergency coordination for CAL FIRE and Cal OES",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = WildfirePipeline()
mock_service = MockWildfireService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "wildfire-response-coordinator",
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
        "service": "wildfire-response-coordinator",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "agents": ["query_agent", "router_agent", "action_agent"],
        "capabilities": ["incident_command", "resource_management", "evacuation_ops", "weather_ops", "utility_coordination", "interagency"],
    }


# ── Incident endpoints ──────────────────────────────────────────────


@app.post("/api/incidents", response_model=IncidentResponse)
async def create_incident(request: CreateIncidentRequest):
    """Create a new incident report."""
    incident = incident_service.create_incident(
        incident_type=request.incident_type,
        name=request.name,
        location=request.location,
        description=request.description,
        severity=request.severity,
    )
    return incident


@app.get("/api/incidents")
async def list_incidents(
    status: str = Query(None, description="Filter by status"),
    type: str = Query(None, description="Filter by incident type"),
):
    """List incidents, optionally filtered."""
    return incident_service.list_incidents(status=status, incident_type=type)


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get incident details by ID."""
    incident = incident_service.get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


# ── Resource endpoints ───────────────────────────────────────────────


@app.post("/api/resources/allocate", response_model=ResourceAllocationResponse)
async def allocate_resources(request: ResourceAllocationRequest):
    """Request resource allocation for an incident."""
    try:
        allocation = resource_service.allocate_resources(
            incident_id=request.incident_id,
            resource_type=request.resource_type,
            quantity=request.quantity,
            from_region=request.from_region,
        )
        return allocation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/resources/available")
async def get_available_resources(
    region: int = Query(None, description="Filter by mutual aid region number"),
    type: str = Query(None, description="Filter by resource type"),
):
    """Check available resources by region."""
    return resource_service.get_available_resources(region=region, resource_type=type)


# ── Evacuation endpoints ────────────────────────────────────────────


@app.get("/api/evacuation/routes", response_model=EvacuationRoute)
async def get_evacuation_routes(zone: str = Query(..., description="Zone ID")):
    """Get evacuation routes for a zone."""
    route = evacuation_service.get_evacuation_routes(zone)
    if route is None:
        raise HTTPException(status_code=404, detail=f"Zone {zone} not found")
    return route


@app.get("/api/evacuation/zones")
async def get_evacuation_zones():
    """Get all evacuation zone statuses."""
    return evacuation_service.get_zone_status()


# ── Weather endpoints ────────────────────────────────────────────────


@app.get("/api/weather/alerts")
async def get_weather_alerts(region: str = Query(None, description="Filter by region name")):
    """Get weather alerts, optionally by region."""
    return weather_service.get_weather_alerts(region=region)


@app.get("/api/weather/fire-conditions")
async def get_fire_weather(location: str = Query(..., description="Location name")):
    """Get fire weather conditions for a location."""
    return weather_service.get_fire_weather(location)


# ── PSPS endpoints ───────────────────────────────────────────────────


@app.get("/api/psps/status")
async def get_psps_status(utility: str = Query(None, description="Utility code (pge, sce, sdge)")):
    """Get Public Safety Power Shutoff status."""
    return psps_service.get_psps_status(utility=utility)


# ── Legacy endpoints (backward compatibility) ────────────────────────


@app.get("/api/weather")
async def get_weather_legacy(county: str | None = None):
    """Get fire weather conditions (legacy)."""
    weather = mock_service.get_weather(county)
    return weather
