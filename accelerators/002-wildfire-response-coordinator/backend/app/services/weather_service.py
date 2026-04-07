"""Mock NWS weather data for Wildfire Response Coordinator."""

from datetime import datetime, timedelta, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _future_iso(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


_MOCK_ALERTS = [
    {
        "alert_id": "NWS-RFW-2025-001",
        "type": "Red Flag Warning",
        "severity": "extreme",
        "regions": ["Butte County", "Plumas County", "Shasta County"],
        "headline": "Red Flag Warning in effect for Northern Sierra",
        "description": "Critical fire weather conditions expected with gusty northeast winds 25-40 mph, low humidity 8-15%, and temperatures above 95°F.",
        "issued": _now_iso(),
        "expires": _future_iso(24),
    },
    {
        "alert_id": "NWS-WA-2025-002",
        "type": "Wind Advisory",
        "severity": "moderate",
        "regions": ["Los Angeles County", "Ventura County"],
        "headline": "Wind Advisory for Santa Ana wind event",
        "description": "Northeast winds 30-45 mph with gusts to 60 mph expected through mountain passes and canyons.",
        "issued": _now_iso(),
        "expires": _future_iso(18),
    },
    {
        "alert_id": "NWS-HEA-2025-003",
        "type": "Heat Advisory",
        "severity": "moderate",
        "regions": ["Fresno County", "Kern County", "Kings County", "Tulare County"],
        "headline": "Heat Advisory for Central Valley",
        "description": "Dangerously hot conditions with temperatures of 105-112°F. Limit outdoor activities.",
        "issued": _now_iso(),
        "expires": _future_iso(48),
    },
    {
        "alert_id": "NWS-FWW-2025-004",
        "type": "Fire Weather Watch",
        "severity": "high",
        "regions": ["San Bernardino County", "Riverside County"],
        "headline": "Fire Weather Watch for Inland Empire mountains",
        "description": "Conditions may become favorable for rapid fire spread with low humidity and gusty winds.",
        "issued": _now_iso(),
        "expires": _future_iso(36),
    },
    {
        "alert_id": "NWS-RFW-2025-005",
        "type": "Red Flag Warning",
        "severity": "extreme",
        "regions": ["Santa Barbara County", "San Luis Obispo County"],
        "headline": "Red Flag Warning for Central Coast ranges",
        "description": "Sundowner winds expected to develop with gusts to 50 mph, single-digit humidity.",
        "issued": _now_iso(),
        "expires": _future_iso(12),
    },
]

_FIRE_WEATHER_BY_LOCATION: dict[str, dict] = {
    "butte county": {
        "location": "Butte County",
        "temperature_f": 102,
        "humidity_pct": 10,
        "wind_speed_mph": 30,
        "wind_direction": "NE",
        "fire_danger_level": "extreme",
    },
    "los angeles county": {
        "location": "Los Angeles County",
        "temperature_f": 95,
        "humidity_pct": 15,
        "wind_speed_mph": 25,
        "wind_direction": "NE",
        "fire_danger_level": "very_high",
    },
    "sacramento county": {
        "location": "Sacramento County",
        "temperature_f": 88,
        "humidity_pct": 35,
        "wind_speed_mph": 8,
        "wind_direction": "SW",
        "fire_danger_level": "moderate",
    },
    "san diego county": {
        "location": "San Diego County",
        "temperature_f": 90,
        "humidity_pct": 20,
        "wind_speed_mph": 18,
        "wind_direction": "E",
        "fire_danger_level": "high",
    },
    "fresno county": {
        "location": "Fresno County",
        "temperature_f": 108,
        "humidity_pct": 8,
        "wind_speed_mph": 12,
        "wind_direction": "NW",
        "fire_danger_level": "very_high",
    },
}

# Default for unknown locations
_DEFAULT_FIRE_WEATHER = {
    "temperature_f": 85,
    "humidity_pct": 30,
    "wind_speed_mph": 10,
    "wind_direction": "W",
    "fire_danger_level": "moderate",
}


def get_weather_alerts(region: str | None = None) -> list[dict]:
    """Get weather alerts, optionally filtered by region name."""
    if region is None:
        return list(_MOCK_ALERTS)
    region_lower = region.lower()
    return [
        a for a in _MOCK_ALERTS
        if any(region_lower in r.lower() for r in a["regions"])
    ]


def get_fire_weather(location: str) -> dict:
    """Get fire weather conditions for a location."""
    key = location.lower().strip()
    if key in _FIRE_WEATHER_BY_LOCATION:
        return dict(_FIRE_WEATHER_BY_LOCATION[key])
    # Try partial match
    for loc_key, data in _FIRE_WEATHER_BY_LOCATION.items():
        if key in loc_key or loc_key in key:
            return dict(data)
    # Return default with the requested location
    result = dict(_DEFAULT_FIRE_WEATHER)
    result["location"] = location
    return result


def is_red_flag_warning(region: str) -> bool:
    """Check if Red Flag Warning is active for a region."""
    alerts = get_weather_alerts(region)
    return any(a["type"] == "Red Flag Warning" for a in alerts)
