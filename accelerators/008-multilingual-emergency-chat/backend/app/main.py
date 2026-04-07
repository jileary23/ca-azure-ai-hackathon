"""Multilingual Emergency Chatbot — FastAPI application."""

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    AirQualityReading,
    Alert,
    ChatRequest,
    ChatResponse,
    Shelter,
    TranslateRequest,
    TranslateResponse,
)
from app.pipeline import process_message
from app.services.air_quality_service import AirQualityService
from app.services.alert_service import AlertService
from app.services.shelter_service import ShelterService
from app.services.translation_service import TranslationService

app = FastAPI(
    title="Multilingual Emergency Chatbot API",
    description="Multilingual emergency information assistant for Cal OES",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alert_service = AlertService()
shelter_service = ShelterService()
aqi_service = AirQualityService()
translation_service = TranslationService()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "multilingual-emergency-chat",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await process_message(request)


@app.get("/api/status")
async def status():
    return {
        "service": "multilingual-emergency-chat",
        "version": "0.1.0",
        "mock_mode": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
        "supported_languages": translation_service.get_supported_languages(),
        "endpoints": [
            "/health",
            "/api/chat",
            "/api/status",
            "/api/alerts",
            "/api/shelters",
            "/api/air-quality",
            "/api/translate",
        ],
    }


@app.get("/api/alerts", response_model=list[Alert])
async def get_alerts(
    zip: str | None = Query(None, description="Filter alerts by ZIP code"),
    lang: str = Query("en", description="Language code for translation"),
):
    """Get emergency alerts, optionally filtered by ZIP code and translated."""
    if zip:
        alerts = await alert_service.get_alerts_by_zip(zip, lang)
    else:
        alerts = await alert_service.get_active_alerts()

    if lang != "en":
        for alert in alerts:
            alert.headline = await translation_service.translate(
                alert.headline, lang
            )
            alert.description = await translation_service.translate(
                alert.description, lang
            )
    return alerts


@app.get("/api/shelters", response_model=list[Shelter])
async def get_shelters(
    zip: str = Query(..., description="ZIP code to search near"),
    radius: int = Query(10, ge=1, le=100, description="Search radius in miles"),
):
    """Find nearby emergency shelters by ZIP code."""
    return await shelter_service.find_shelters(zip, radius)


@app.get("/api/air-quality", response_model=AirQualityReading)
async def get_air_quality(
    zip: str = Query(..., description="ZIP code to check"),
):
    """Get air quality index for a ZIP code."""
    return await aqi_service.get_aqi(zip)


@app.post("/api/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translate text to target language."""
    translated = await translation_service.translate(
        request.text, request.target_lang, request.source_lang
    )
    return TranslateResponse(
        translated_text=translated,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )
