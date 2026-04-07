"""Pydantic v2 models for Multilingual Emergency Chatbot."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    session_id: str | None = None
    location: str | None = None


class Citation(BaseModel):
    source: str
    text: str
    url: str | None = None


class EmergencyQuery(BaseModel):
    raw_input: str
    intent: str = "general_info"
    language: str = "en"
    location: str | None = None
    emergency_type: str | None = None
    entities: dict = Field(default_factory=dict)


class EmergencyAlert(BaseModel):
    alert_id: str
    title: str
    description: str
    severity: Literal["extreme", "severe", "moderate", "minor"]
    emergency_type: str
    affected_areas: list[str] = Field(default_factory=list)
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    instructions: str = ""
    source: str = "Cal OES"


class EvacuationOrder(BaseModel):
    order_id: str
    zone_name: str
    status: Literal["mandatory", "warning", "advisory", "lifted"]
    issued_at: datetime | None = None
    instructions: str = ""
    routes: list[str] = Field(default_factory=list)


class ShelterInfo(BaseModel):
    shelter_id: str
    name: str
    address: str
    city: str
    county: str
    capacity: int
    current_occupancy: int = 0
    accepts_pets: bool = False
    ada_accessible: bool = True
    status: str = "open"
    distance_miles: float | None = None


class AirQualityReport(BaseModel):
    location: str
    aqi: int
    category: Literal[
        "good", "moderate", "unhealthy_sensitive",
        "unhealthy", "very_unhealthy", "hazardous",
    ]
    pollutant: str = "PM2.5"
    health_guidance: str = ""
    forecast: list[dict] = Field(default_factory=list)


class AgentResponse(BaseModel):
    intent: str
    response_text: str
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    data: dict | None = None
    requires_translation: bool = False


class RoutingDecision(BaseModel):
    department: str
    priority: Literal["low", "medium", "high", "critical"]
    reason: str
    escalate: bool = False


class ChatResponse(BaseModel):
    response: str
    translated_response: str | None = None
    language: str = "en"
    confidence: float = 0.0
    citations: list[Citation] = Field(default_factory=list)
    alerts: list[EmergencyAlert] | None = None
    shelters: list[ShelterInfo] | None = None


# ---- Domain endpoint models ------------------------------------------------

class Alert(BaseModel):
    id: str
    type: Literal["fire", "earthquake", "flood", "tsunami"]
    severity: Literal["extreme", "severe", "moderate", "minor"]
    headline: str
    description: str
    areas_affected: list[str] = Field(default_factory=list)
    issued_at: datetime | None = None
    expires_at: datetime | None = None


class Shelter(BaseModel):
    id: str
    name: str
    address: str
    city: str
    zip_code: str
    lat: float
    lng: float
    capacity: int
    current_occupancy: int = 0
    accepts_pets: bool = False
    ada_accessible: bool = True
    services: list[str] = Field(default_factory=list)
    phone: str = ""
    distance_miles: float | None = None


class AirQualityReading(BaseModel):
    zip_code: str
    aqi: int = Field(ge=0)
    category: str
    dominant_pollutant: str = "PM2.5"
    health_guidance: str = ""
    updated_at: datetime | None = None


class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "en"


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
