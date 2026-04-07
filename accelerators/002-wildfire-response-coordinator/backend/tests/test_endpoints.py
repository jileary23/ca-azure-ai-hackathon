"""Tests for domain API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.services import incident_service, resource_service

# Reset services before importing app to get clean state
incident_service.reset()
resource_service.reset()

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_services():
    incident_service.reset()
    resource_service.reset()
    yield
    incident_service.reset()
    resource_service.reset()


class TestIncidentEndpoints:
    def test_create_incident(self):
        resp = client.post("/api/incidents", json={
            "incident_type": "wildfire",
            "name": "API Test Fire",
            "location": "Test Location",
            "description": "Test description",
            "severity": "high",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["incident_id"].startswith("INC-")
        assert data["lead_agency"] == "CAL FIRE"

    def test_list_incidents(self):
        resp = client.get("/api/incidents")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 4  # seeded

    def test_list_filter_by_type(self):
        resp = client.get("/api/incidents?type=wildfire")
        assert resp.status_code == 200
        data = resp.json()
        assert all(i["incident_type"] == "wildfire" for i in data)

    def test_get_incident(self):
        # Create one first
        create_resp = client.post("/api/incidents", json={
            "incident_type": "flood",
            "name": "Flood Test",
            "location": "River",
            "description": "Big flood",
        })
        iid = create_resp.json()["incident_id"]
        resp = client.get(f"/api/incidents/{iid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Flood Test"

    def test_get_incident_not_found(self):
        resp = client.get("/api/incidents/INC-NONE-999")
        assert resp.status_code == 404


class TestResourceEndpoints:
    def test_available_resources(self):
        resp = client.get("/api/resources/available")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_available_resources_by_region(self):
        resp = client.get("/api/resources/available?region=6")
        assert resp.status_code == 200
        data = resp.json()
        assert all(r["region"] == 6 for r in data)

    def test_available_resources_by_type(self):
        resp = client.get("/api/resources/available?type=helicopters")
        assert resp.status_code == 200
        data = resp.json()
        assert all(r["resource_type"] == "helicopters" for r in data)

    def test_allocate_resources(self):
        resp = client.post("/api/resources/allocate", json={
            "incident_id": "INC-2025-001",
            "resource_type": "fire_engines",
            "quantity": 5,
            "from_region": 6,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["allocation_id"].startswith("ALLOC-")
        assert data["status"] == "dispatched"

    def test_allocate_invalid_type(self):
        resp = client.post("/api/resources/allocate", json={
            "incident_id": "INC-1",
            "resource_type": "tanks",
            "quantity": 1,
        })
        assert resp.status_code == 400


class TestEvacuationEndpoints:
    def test_get_routes(self):
        resp = client.get("/api/evacuation/routes?zone=zone-b")
        assert resp.status_code == 200
        data = resp.json()
        assert data["zone_id"] == "zone-b"
        assert data["primary_route"] != ""

    def test_get_routes_not_found(self):
        resp = client.get("/api/evacuation/routes?zone=zone-zz")
        assert resp.status_code == 404

    def test_get_zones(self):
        resp = client.get("/api/evacuation/zones")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5


class TestWeatherEndpoints:
    def test_all_alerts(self):
        resp = client.get("/api/weather/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 5

    def test_alerts_by_region(self):
        resp = client.get("/api/weather/alerts?region=Butte+County")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_fire_conditions(self):
        resp = client.get("/api/weather/fire-conditions?location=Butte+County")
        assert resp.status_code == 200
        data = resp.json()
        assert data["fire_danger_level"] == "extreme"

    def test_fire_conditions_required(self):
        resp = client.get("/api/weather/fire-conditions")
        assert resp.status_code == 422  # missing required param


class TestPSPSEndpoints:
    def test_all_status(self):
        resp = client.get("/api/psps/status")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_specific_utility(self):
        resp = client.get("/api/psps/status?utility=pge")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"


class TestLegacyEndpoints:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_status(self):
        resp = client.get("/api/status")
        assert resp.status_code == 200

    def test_legacy_weather(self):
        resp = client.get("/api/weather")
        assert resp.status_code == 200
