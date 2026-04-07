"""Mock AQI service for multilingual emergency chat."""

import os
from datetime import datetime, timezone

from app.models.schemas import AirQualityReading

# ZIP → mock AQI data
_MOCK_DATA: dict[str, dict] = {
    "90210": {"aqi": 68, "dominant_pollutant": "PM2.5"},
    "90015": {"aqi": 72, "dominant_pollutant": "PM2.5"},
    "94103": {"aqi": 45, "dominant_pollutant": "O3"},
    "95814": {"aqi": 142, "dominant_pollutant": "PM2.5"},
    "95815": {"aqi": 138, "dominant_pollutant": "PM2.5"},
    "92101": {"aqi": 35, "dominant_pollutant": "O3"},
    "93721": {"aqi": 178, "dominant_pollutant": "PM2.5"},
    "93301": {"aqi": 205, "dominant_pollutant": "PM2.5"},
    "91101": {"aqi": 95, "dominant_pollutant": "PM2.5"},
}


def _category_for_aqi(aqi: int) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def _guidance_for_aqi(aqi: int) -> str:
    if aqi <= 50:
        return "Air quality is satisfactory with little or no risk."
    if aqi <= 100:
        return "Acceptable air quality. Sensitive individuals should limit prolonged outdoor exertion."
    if aqi <= 150:
        return "Members of sensitive groups may experience health effects. General public is less likely to be affected."
    if aqi <= 200:
        return "Everyone may begin to experience health effects. Sensitive groups may experience more serious effects."
    if aqi <= 300:
        return "Health alert: everyone may experience more serious health effects. Avoid outdoor exertion."
    return "Health warning of emergency conditions. The entire population is likely to be affected. Stay indoors."


class AirQualityService:
    """Returns AQI data for a ZIP code (mock when USE_MOCK_SERVICES=true)."""

    def __init__(self) -> None:
        self.mock = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

    async def get_aqi(self, zip_code: str) -> AirQualityReading:
        if self.mock:
            data = _MOCK_DATA.get(zip_code, {"aqi": 55, "dominant_pollutant": "O3"})
            aqi = data["aqi"]
            return AirQualityReading(
                zip_code=zip_code,
                aqi=aqi,
                category=_category_for_aqi(aqi),
                dominant_pollutant=data["dominant_pollutant"],
                health_guidance=_guidance_for_aqi(aqi),
                updated_at=datetime.now(tz=timezone.utc),
            )
        raise NotImplementedError("Real AQI service not configured")
