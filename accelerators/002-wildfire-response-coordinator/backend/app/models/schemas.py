"""Pydantic v2 models for Wildfire Response Coordinator."""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Request / Response ---

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    incident_id: str | None = None


class Citation(BaseModel):
    source: str
    text: str
    agency: str | None = None


class IncidentSummary(BaseModel):
    incident_id: str
    name: str
    incident_type: str
    severity: str
    location: str
    containment_pct: float | None = None
    status: str
    lead_agency: str


class ResourceAllocation(BaseModel):
    resource_id: str
    resource_type: str  # engine, crew, helicopter, dozer, water_tender, air_tanker
    quantity: int = 1
    agency: str = ""
    status: str = "available"  # available, deployed, en_route, committed
    eta_minutes: int | None = None
    mutual_aid_region: int = 1


class EvacuationZone(BaseModel):
    zone_id: str
    zone_name: str
    status: str = "warning"  # warning, order, shelter_in_place, lifted
    population: int = 0
    routes: list[str] = Field(default_factory=list)
    shelters: list[str] = Field(default_factory=list)


class EvacuationInfo(BaseModel):
    zones: list[EvacuationZone] = Field(default_factory=list)
    total_evacuated: int = 0
    shelters_open: int = 0


class ChatResponse(BaseModel):
    response: str
    confidence: float
    citations: list[Citation] = Field(default_factory=list)
    incident: IncidentSummary | None = None
    resources: list[ResourceAllocation] | None = None
    evacuation: EvacuationInfo | None = None


# --- Internal Agent Models ---

class IncidentQuery(BaseModel):
    raw_input: str
    intent: str = "general_info"
    entities: dict = Field(default_factory=dict)
    incident_type: str | None = None


class Incident(BaseModel):
    incident_id: str
    name: str
    incident_type: str = "wildfire"  # wildfire, structure_fire, flood, earthquake, hazmat
    severity: str = "moderate"  # minor, moderate, major, catastrophic
    location: str = ""
    county: str = ""
    acres_burned: float | None = None
    containment_pct: float | None = None
    lead_agency: str = "CAL FIRE"
    status: str = "active"  # active, contained, controlled, out
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    mutual_aid_region: int = 1


class WeatherCondition(BaseModel):
    location: str
    temperature_f: float
    humidity_pct: float
    wind_speed_mph: float
    wind_direction: str
    red_flag_warning: bool = False
    fire_weather_watch: bool = False
    forecast_summary: str = ""


class PSPSEvent(BaseModel):
    event_id: str
    utility: str  # PGE, SCE, SDGE
    status: str = "planned"  # planned, active, restored
    affected_customers: int = 0
    start_time: datetime = Field(default_factory=datetime.utcnow)
    estimated_restoration: datetime | None = None
    affected_areas: list[str] = Field(default_factory=list)


class AgencyAssignment(BaseModel):
    agency: str  # CAL_FIRE, Cal_OES, County_FD, CHP, USFS, NWS
    role: str = ""
    contact: str = ""
    resources_committed: int = 0


class RoutingDecision(BaseModel):
    destination: str
    priority: str = "medium"
    escalate: bool = False
    escalation_reason: str | None = None


class AgentResponse(BaseModel):
    response: str
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    incident: IncidentSummary | None = None
    resources: list[ResourceAllocation] | None = None
    evacuation: EvacuationInfo | None = None


# --- Domain Endpoint Models ---

class CreateIncidentRequest(BaseModel):
    incident_type: str
    name: str
    location: str
    description: str
    severity: str = "high"


class IncidentResponse(BaseModel):
    incident_id: str
    incident_type: str
    name: str
    location: str
    description: str
    severity: str
    status: str
    lead_agency: str
    created_at: str
    updated_at: str
    resources: list = Field(default_factory=list)


class ResourceAllocationRequest(BaseModel):
    incident_id: str
    resource_type: str
    quantity: int
    from_region: int | None = None


class ResourceAllocationResponse(BaseModel):
    allocation_id: str
    incident_id: str
    resource_type: str
    quantity: int
    from_region: int
    status: str


class EvacuationRoute(BaseModel):
    zone_id: str
    zone_name: str
    population: int
    primary_route: str
    alternate_route: str
    status: str
    estimated_time_minutes: int


class WeatherAlert(BaseModel):
    alert_id: str
    type: str
    severity: str
    regions: list[str]
    headline: str
    description: str
    issued: str
    expires: str


class FireWeather(BaseModel):
    location: str
    temperature_f: int
    humidity_pct: int
    wind_speed_mph: int
    wind_direction: str
    fire_danger_level: str


class PSPSStatus(BaseModel):
    utility_code: str
    utility_name: str
    status: str
    affected_areas: list[str]
    estimated_restoration: str | None = None
