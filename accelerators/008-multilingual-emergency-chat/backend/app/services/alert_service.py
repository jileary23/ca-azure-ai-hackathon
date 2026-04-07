"""Mock emergency alert service for multilingual emergency chat."""

import os
from datetime import datetime, timedelta, timezone

from app.models.schemas import Alert


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


MOCK_ALERTS: list[dict] = [
    {
        "id": "ALERT-CA-001",
        "type": "fire",
        "severity": "extreme",
        "headline": "Wildfire Evacuation Order — Los Angeles County",
        "description": "A fast-moving wildfire in the Santa Monica Mountains has triggered mandatory evacuations for ZIP codes 90210, 90211, and 90212.",
        "areas_affected": ["90210", "90211", "90212", "Beverly Hills", "Los Angeles County"],
    },
    {
        "id": "ALERT-CA-002",
        "type": "earthquake",
        "severity": "severe",
        "headline": "Earthquake Advisory — San Diego County",
        "description": "A 5.1 magnitude earthquake was recorded near Escondido. Aftershocks expected.",
        "areas_affected": ["92101", "92102", "92025", "San Diego", "Escondido"],
    },
    {
        "id": "ALERT-CA-003",
        "type": "flood",
        "severity": "moderate",
        "headline": "Flash Flood Warning — Sacramento Region",
        "description": "Heavy rainfall expected to cause flash flooding in low-lying areas near the American River.",
        "areas_affected": ["95814", "95816", "95818", "Sacramento"],
    },
    {
        "id": "ALERT-CA-004",
        "type": "tsunami",
        "severity": "severe",
        "headline": "Tsunami Watch — Northern California Coast",
        "description": "A tsunami watch has been issued following a 7.0 earthquake in the Pacific Ocean.",
        "areas_affected": ["95531", "95501", "Crescent City", "Eureka"],
    },
    {
        "id": "ALERT-CA-005",
        "type": "fire",
        "severity": "moderate",
        "headline": "Spare the Air Alert — Central Valley",
        "description": "Wildfire smoke has degraded air quality across the Central Valley. Sensitive groups should stay indoors.",
        "areas_affected": ["93721", "93301", "Fresno", "Bakersfield"],
    },
]


def _build_alerts() -> list[Alert]:
    now = _now()
    alerts: list[Alert] = []
    for i, raw in enumerate(MOCK_ALERTS):
        alerts.append(
            Alert(
                id=raw["id"],
                type=raw["type"],
                severity=raw["severity"],
                headline=raw["headline"],
                description=raw["description"],
                areas_affected=raw["areas_affected"],
                issued_at=now - timedelta(hours=i + 1),
                expires_at=now + timedelta(hours=24 - i),
            )
        )
    return alerts


class AlertService:
    """Provides emergency alerts (mock when USE_MOCK_SERVICES=true)."""

    def __init__(self) -> None:
        self.mock = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

    async def get_alerts_by_zip(self, zip_code: str, lang: str = "en") -> list[Alert]:
        if self.mock:
            return [
                a for a in _build_alerts()
                if zip_code in a.areas_affected
            ]
        raise NotImplementedError("Real alert service not configured")

    async def get_active_alerts(self) -> list[Alert]:
        if self.mock:
            return _build_alerts()
        raise NotImplementedError("Real alert service not configured")
