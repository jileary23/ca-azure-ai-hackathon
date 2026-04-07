"""Resource allocation across Cal OES mutual aid regions."""

import uuid
from datetime import datetime, timezone

MUTUAL_AID_REGIONS = {
    1: {
        "name": "Region I",
        "counties": ["Del Norte", "Humboldt", "Lassen", "Modoc", "Shasta", "Siskiyou", "Tehama", "Trinity"],
        "coordinator": "Redding OES",
    },
    2: {
        "name": "Region II",
        "counties": [
            "Alpine", "Amador", "Butte", "Calaveras", "Colusa", "El Dorado", "Glenn",
            "Lake", "Napa", "Nevada", "Placer", "Plumas", "Sacramento", "San Joaquin",
            "Sierra", "Solano", "Stanislaus", "Sutter", "Tuolumne", "Yolo", "Yuba",
        ],
        "coordinator": "Sacramento OES",
    },
    3: {
        "name": "Region III",
        "counties": [
            "Alameda", "Contra Costa", "Marin", "Monterey", "San Benito",
            "San Francisco", "San Mateo", "Santa Clara", "Santa Cruz", "Sonoma",
        ],
        "coordinator": "Oakland OES",
    },
    4: {
        "name": "Region IV",
        "counties": ["Fresno", "Inyo", "Kern", "Kings", "Madera", "Mariposa", "Merced", "Mono", "Tulare"],
        "coordinator": "Fresno OES",
    },
    5: {
        "name": "Region V",
        "counties": ["San Luis Obispo", "Santa Barbara", "Ventura"],
        "coordinator": "Ventura OES",
    },
    6: {
        "name": "Region VI",
        "counties": ["Imperial", "Los Angeles", "Orange", "Riverside", "San Bernardino", "San Diego"],
        "coordinator": "Los Angeles OES",
    },
}

RESOURCE_TYPES = [
    "fire_engines", "hand_crews", "air_tankers", "helicopters",
    "dozers", "water_tenders", "ambulances", "search_rescue",
]

# Base availability per region (units)
_BASE_AVAILABILITY: dict[int, dict[str, int]] = {
    1: {"fire_engines": 8, "hand_crews": 4, "air_tankers": 1, "helicopters": 2, "dozers": 3, "water_tenders": 4, "ambulances": 6, "search_rescue": 2},
    2: {"fire_engines": 15, "hand_crews": 8, "air_tankers": 2, "helicopters": 3, "dozers": 5, "water_tenders": 6, "ambulances": 10, "search_rescue": 3},
    3: {"fire_engines": 12, "hand_crews": 6, "air_tankers": 1, "helicopters": 2, "dozers": 4, "water_tenders": 5, "ambulances": 12, "search_rescue": 4},
    4: {"fire_engines": 10, "hand_crews": 6, "air_tankers": 2, "helicopters": 2, "dozers": 6, "water_tenders": 5, "ambulances": 8, "search_rescue": 2},
    5: {"fire_engines": 6, "hand_crews": 3, "air_tankers": 1, "helicopters": 1, "dozers": 2, "water_tenders": 3, "ambulances": 5, "search_rescue": 1},
    6: {"fire_engines": 20, "hand_crews": 10, "air_tankers": 3, "helicopters": 4, "dozers": 6, "water_tenders": 8, "ambulances": 15, "search_rescue": 5},
}

_allocations: list[dict] = []


def allocate_resources(
    incident_id: str,
    resource_type: str,
    quantity: int,
    from_region: int | None = None,
) -> dict:
    """Request resource allocation for an incident."""
    if resource_type not in RESOURCE_TYPES:
        raise ValueError(f"Unknown resource type: {resource_type}")
    region = from_region or 2  # default to Region II (Sacramento)
    if region not in MUTUAL_AID_REGIONS:
        raise ValueError(f"Unknown region: {region}")

    allocation = {
        "allocation_id": f"ALLOC-{uuid.uuid4().hex[:8].upper()}",
        "incident_id": incident_id,
        "resource_type": resource_type,
        "quantity": quantity,
        "from_region": region,
        "status": "dispatched",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _allocations.append(allocation)
    return allocation


def get_available_resources(
    region: int | None = None,
    resource_type: str | None = None,
) -> list[dict]:
    """Check available resources by region."""
    results = []
    regions_to_check = [region] if region else list(MUTUAL_AID_REGIONS.keys())

    for r in regions_to_check:
        if r not in _BASE_AVAILABILITY:
            continue
        avail = _BASE_AVAILABILITY[r]
        types_to_check = [resource_type] if resource_type else RESOURCE_TYPES
        for rt in types_to_check:
            qty = avail.get(rt, 0)
            if qty > 0:
                results.append({
                    "region": r,
                    "region_name": MUTUAL_AID_REGIONS[r]["name"],
                    "coordinator": MUTUAL_AID_REGIONS[r]["coordinator"],
                    "resource_type": rt,
                    "available": qty,
                })
    return results


def get_allocation_status(incident_id: str) -> list[dict]:
    """Get all resource allocations for an incident."""
    return [a for a in _allocations if a["incident_id"] == incident_id]


def reset() -> None:
    """Reset state — for testing."""
    _allocations.clear()
