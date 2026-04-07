"""Evacuation route optimization (mock) for Wildfire Response Coordinator."""

import math

EVACUATION_ZONES: dict[str, dict] = {
    "zone-a": {
        "name": "Zone A - Foothill",
        "population": 15000,
        "primary_route": "SR-2 West",
        "alternate_route": "Angeles Crest Hwy",
        "status": "warning",
    },
    "zone-b": {
        "name": "Zone B - Canyon",
        "population": 8000,
        "primary_route": "Topanga Canyon Blvd South",
        "alternate_route": "PCH East",
        "status": "order",
    },
    "zone-c": {
        "name": "Zone C - Valley",
        "population": 25000,
        "primary_route": "US-101 South",
        "alternate_route": "SR-118 West",
        "status": "none",
    },
    "zone-d": {
        "name": "Zone D - Coastal",
        "population": 12000,
        "primary_route": "PCH South",
        "alternate_route": "SR-1 North",
        "status": "warning",
    },
    "zone-e": {
        "name": "Zone E - Urban",
        "population": 40000,
        "primary_route": "I-5 South",
        "alternate_route": "I-405 South",
        "status": "none",
    },
}

# Vehicles per hour per route (mock capacity)
_ROUTE_CAPACITY_VPH = 1200


def get_evacuation_routes(zone_id: str) -> dict | None:
    """Get evacuation routes for a zone."""
    zone = EVACUATION_ZONES.get(zone_id)
    if zone is None:
        return None
    return {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "population": zone["population"],
        "primary_route": zone["primary_route"],
        "alternate_route": zone["alternate_route"],
        "status": zone["status"],
        "estimated_time_minutes": estimate_evacuation_time(zone_id),
    }


def get_zone_status(zone_id: str | None = None) -> list[dict]:
    """Get evacuation zone status (order/warning/none)."""
    if zone_id:
        zone = EVACUATION_ZONES.get(zone_id)
        if zone is None:
            return []
        return [{
            "zone_id": zone_id,
            "zone_name": zone["name"],
            "population": zone["population"],
            "status": zone["status"],
            "primary_route": zone["primary_route"],
            "alternate_route": zone["alternate_route"],
            "estimated_time_minutes": estimate_evacuation_time(zone_id),
        }]
    return [
        {
            "zone_id": zid,
            "zone_name": z["name"],
            "population": z["population"],
            "status": z["status"],
            "primary_route": z["primary_route"],
            "alternate_route": z["alternate_route"],
            "estimated_time_minutes": estimate_evacuation_time(zid),
        }
        for zid, z in EVACUATION_ZONES.items()
    ]


def estimate_evacuation_time(zone_id: str) -> int:
    """Estimate evacuation time in minutes based on population and route capacity.

    Simple model: assume 2.5 people per vehicle, two routes active.
    """
    zone = EVACUATION_ZONES.get(zone_id)
    if zone is None:
        return 0
    population = zone["population"]
    vehicles_needed = math.ceil(population / 2.5)
    # Two routes available
    combined_capacity_vph = _ROUTE_CAPACITY_VPH * 2
    hours = vehicles_needed / combined_capacity_vph
    return max(30, math.ceil(hours * 60))
