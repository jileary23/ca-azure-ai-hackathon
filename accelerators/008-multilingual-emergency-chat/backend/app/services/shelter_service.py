"""Mock shelter locator service for multilingual emergency chat."""

import os

from app.models.schemas import Shelter

MOCK_SHELTERS: list[dict] = [
    {
        "id": "SH-LA-001",
        "name": "Los Angeles Convention Center",
        "address": "1201 S Figueroa St",
        "city": "Los Angeles",
        "zip_code": "90015",
        "lat": 34.0404,
        "lng": -118.2696,
        "capacity": 1500,
        "current_occupancy": 342,
        "accepts_pets": False,
        "ada_accessible": True,
        "services": ["meals", "cots", "medical", "wifi"],
        "phone": "(213) 741-1151",
    },
    {
        "id": "SH-LA-002",
        "name": "Beverly Hills Community Center",
        "address": "325 S La Cienega Blvd",
        "city": "Beverly Hills",
        "zip_code": "90211",
        "lat": 34.0624,
        "lng": -118.3764,
        "capacity": 400,
        "current_occupancy": 189,
        "accepts_pets": True,
        "ada_accessible": True,
        "services": ["meals", "cots", "pet area", "charging stations"],
        "phone": "(310) 285-1000",
    },
    {
        "id": "SH-SF-001",
        "name": "Moscone Center Shelter",
        "address": "747 Howard St",
        "city": "San Francisco",
        "zip_code": "94103",
        "lat": 37.7842,
        "lng": -122.4016,
        "capacity": 1000,
        "current_occupancy": 156,
        "accepts_pets": True,
        "ada_accessible": True,
        "services": ["meals", "cots", "medical", "mental health", "wifi"],
        "phone": "(415) 554-6000",
    },
    {
        "id": "SH-SAC-001",
        "name": "Cal Expo Evacuation Center",
        "address": "1600 Exposition Blvd",
        "city": "Sacramento",
        "zip_code": "95815",
        "lat": 38.5912,
        "lng": -121.4255,
        "capacity": 2000,
        "current_occupancy": 523,
        "accepts_pets": True,
        "ada_accessible": True,
        "services": ["meals", "cots", "medical", "pet area", "laundry"],
        "phone": "(916) 263-3000",
    },
    {
        "id": "SH-SAC-002",
        "name": "Sacramento Convention Center",
        "address": "1400 J St",
        "city": "Sacramento",
        "zip_code": "95814",
        "lat": 38.5795,
        "lng": -121.4942,
        "capacity": 1200,
        "current_occupancy": 89,
        "accepts_pets": False,
        "ada_accessible": True,
        "services": ["meals", "cots", "wifi", "charging stations"],
        "phone": "(916) 808-5291",
    },
    {
        "id": "SH-SD-001",
        "name": "San Diego Convention Center",
        "address": "111 W Harbor Dr",
        "city": "San Diego",
        "zip_code": "92101",
        "lat": 32.7066,
        "lng": -117.1626,
        "capacity": 800,
        "current_occupancy": 210,
        "accepts_pets": False,
        "ada_accessible": True,
        "services": ["meals", "cots", "medical"],
        "phone": "(619) 525-5000",
    },
    {
        "id": "SH-LA-003",
        "name": "Pasadena Civic Auditorium",
        "address": "300 E Green St",
        "city": "Pasadena",
        "zip_code": "91101",
        "lat": 34.1455,
        "lng": -118.1431,
        "capacity": 600,
        "current_occupancy": 75,
        "accepts_pets": True,
        "ada_accessible": True,
        "services": ["meals", "cots", "pet area", "childcare"],
        "phone": "(626) 449-7360",
    },
    {
        "id": "SH-SF-002",
        "name": "Oakland Arena Emergency Shelter",
        "address": "7000 Coliseum Way",
        "city": "Oakland",
        "zip_code": "94621",
        "lat": 37.7503,
        "lng": -122.2005,
        "capacity": 900,
        "current_occupancy": 0,
        "accepts_pets": True,
        "ada_accessible": True,
        "services": ["meals", "cots", "medical", "wifi"],
        "phone": "(510) 569-2121",
    },
]

# Simple ZIP → lat/lng lookup for distance calculations
ZIP_COORDS: dict[str, tuple[float, float]] = {
    "90015": (34.0404, -118.2696),
    "90210": (34.0901, -118.4065),
    "90211": (34.0624, -118.3764),
    "94103": (37.7749, -122.4194),
    "95814": (38.5816, -121.4944),
    "95815": (38.5912, -121.4255),
    "92101": (32.7157, -117.1611),
    "91101": (34.1478, -118.1445),
    "94621": (37.7503, -122.2005),
    "93721": (36.7378, -119.7871),
}


def _approx_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Rough haversine-like approximation in miles (good enough for mock)."""
    import math
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return c * 3956  # Earth radius in miles


class ShelterService:
    """Finds nearby emergency shelters (mock when USE_MOCK_SERVICES=true)."""

    def __init__(self) -> None:
        self.mock = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

    async def find_shelters(self, zip_code: str, radius_miles: int = 10) -> list[Shelter]:
        if self.mock:
            origin = ZIP_COORDS.get(zip_code, (34.0522, -118.2437))  # default LA
            results: list[Shelter] = []
            for s in MOCK_SHELTERS:
                dist = _approx_distance(origin[0], origin[1], s["lat"], s["lng"])
                if dist <= radius_miles:
                    results.append(Shelter(**s, distance_miles=round(dist, 1)))
            # If nothing in radius, return all sorted by distance
            if not results:
                for s in MOCK_SHELTERS:
                    dist = _approx_distance(origin[0], origin[1], s["lat"], s["lng"])
                    results.append(Shelter(**s, distance_miles=round(dist, 1)))
                results.sort(key=lambda x: x.distance_miles or 999)
            return results
        raise NotImplementedError("Real shelter service not configured")
