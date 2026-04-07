"""Tests for incident lifecycle management."""

import pytest
from app.services import incident_service


@pytest.fixture(autouse=True)
def reset_state():
    incident_service.reset()
    yield
    incident_service.reset()


class TestCreateIncident:
    def test_create_wildfire(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="Test Fire",
            location="Butte County", description="Brush fire", severity="critical",
        )
        assert inc["incident_id"].startswith("INC-")
        assert inc["incident_type"] == "wildfire"
        assert inc["lead_agency"] == "CAL FIRE"
        assert inc["status"] == "active"
        assert inc["severity"] == "critical"

    def test_create_earthquake(self):
        inc = incident_service.create_incident(
            incident_type="earthquake", name="Bay Quake",
            location="Oakland", description="5.0 quake",
        )
        assert inc["lead_agency"] == "Cal OES"

    def test_create_flood(self):
        inc = incident_service.create_incident(
            incident_type="flood", name="River Flood",
            location="Sacramento", description="Flooding",
        )
        assert inc["lead_agency"] == "DWR"

    def test_create_hazmat(self):
        inc = incident_service.create_incident(
            incident_type="hazmat", name="Spill",
            location="I-5", description="Chemical spill",
        )
        assert inc["lead_agency"] == "CHP"

    def test_create_unknown_type(self):
        inc = incident_service.create_incident(
            incident_type="meteor", name="Meteor Strike",
            location="Desert", description="Meteor",
        )
        assert inc["lead_agency"] == "Cal OES"

    def test_sequential_ids(self):
        inc1 = incident_service.create_incident(
            incident_type="wildfire", name="Fire 1",
            location="A", description="D1",
        )
        inc2 = incident_service.create_incident(
            incident_type="wildfire", name="Fire 2",
            location="B", description="D2",
        )
        assert inc1["incident_id"] != inc2["incident_id"]

    def test_created_at_set(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="F",
            location="L", description="D",
        )
        assert "created_at" in inc
        assert "updated_at" in inc

    def test_resources_empty(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="F",
            location="L", description="D",
        )
        assert inc["resources"] == []


class TestGetIncident:
    def test_get_existing(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="Test",
            location="L", description="D",
        )
        fetched = incident_service.get_incident(inc["incident_id"])
        assert fetched is not None
        assert fetched["name"] == "Test"

    def test_get_nonexistent(self):
        # Seed first so seed doesn't change the result
        incident_service.list_incidents()
        result = incident_service.get_incident("INC-9999-999")
        assert result is None

    def test_get_seeded_incidents(self):
        # Triggering list_incidents seeds the data
        incidents = incident_service.list_incidents()
        assert len(incidents) >= 4
        first_id = incidents[0]["incident_id"]
        fetched = incident_service.get_incident(first_id)
        assert fetched is not None


class TestUpdateIncident:
    def test_update_status(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="F",
            location="L", description="D",
        )
        updated = incident_service.update_incident(inc["incident_id"], {"status": "contained"})
        assert updated is not None
        assert updated["status"] == "contained"

    def test_update_severity(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="F",
            location="L", description="D",
        )
        updated = incident_service.update_incident(inc["incident_id"], {"severity": "critical"})
        assert updated["severity"] == "critical"

    def test_update_nonexistent(self):
        result = incident_service.update_incident("INC-NONE-000", {"status": "closed"})
        assert result is None

    def test_update_ignores_disallowed_fields(self):
        inc = incident_service.create_incident(
            incident_type="wildfire", name="F",
            location="L", description="D",
        )
        updated = incident_service.update_incident(inc["incident_id"], {"incident_id": "HACKED"})
        assert updated["incident_id"] == inc["incident_id"]


class TestListIncidents:
    def test_list_all(self):
        incidents = incident_service.list_incidents()
        assert len(incidents) >= 4  # seeded

    def test_filter_by_status(self):
        incidents = incident_service.list_incidents(status="active")
        assert all(i["status"] == "active" for i in incidents)

    def test_filter_by_type(self):
        incidents = incident_service.list_incidents(incident_type="wildfire")
        assert len(incidents) >= 1
        assert all(i["incident_type"] == "wildfire" for i in incidents)

    def test_filter_nonexistent_type(self):
        incidents = incident_service.list_incidents(incident_type="tornado")
        assert incidents == []


class TestIncidentTypes:
    def test_all_types_have_lead_agency(self):
        for t, info in incident_service.INCIDENT_TYPES.items():
            assert "lead_agency" in info
            assert "priority" in info

    def test_wildfire_is_critical(self):
        assert incident_service.INCIDENT_TYPES["wildfire"]["priority"] == "critical"
