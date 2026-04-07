"""Tests for SLA tracking service."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import PermitApplication
from app.services.sla_service import calculate_sla, get_sla_status

client = TestClient(app)


# --- Unit tests ---


def test_base_sla_residential():
    assert calculate_sla("residential_construction") == 30


def test_base_sla_commercial():
    assert calculate_sla("commercial_construction") == 45


def test_base_sla_environmental():
    assert calculate_sla("environmental_review") == 60


def test_base_sla_electrical():
    assert calculate_sla("electrical") == 10


def test_sla_with_environmental_constraint():
    days = calculate_sla("residential_construction", ["environmental_review"])
    assert days == 30 + 15


def test_sla_with_coastal_constraint():
    days = calculate_sla("residential_construction", ["coastal_zone"])
    assert days == 30 + 10


def test_sla_with_historic_constraint():
    days = calculate_sla("residential_construction", ["historic_district"])
    assert days == 30 + 20


def test_sla_with_multi_agency():
    days = calculate_sla("residential_construction", ["multi_agency"])
    assert days == 30 + 10


def test_sla_stacks_constraints():
    days = calculate_sla(
        "residential_construction",
        ["environmental_review", "coastal_zone", "historic_district"],
    )
    assert days == 30 + 15 + 10 + 20


def test_sla_unknown_constraint_ignored():
    days = calculate_sla("residential_construction", ["unknown_stuff"])
    assert days == 30


def test_get_sla_status_on_track():
    app_obj = PermitApplication(
        app_id="PRM-TEST-001",
        applicant_name="Test",
        project_type="residential_construction",
        project_description="Test",
        address="123 Test St",
        status="submitted",
        submitted_at=datetime.now(),
        estimated_completion=datetime.now() + timedelta(days=25),
    )
    status = get_sla_status(app_obj)
    assert status.status == "on_track"
    assert status.days_remaining > 5


def test_get_sla_status_at_risk():
    app_obj = PermitApplication(
        app_id="PRM-TEST-002",
        applicant_name="Test",
        project_type="residential_construction",
        project_description="Test",
        address="123 Test St",
        status="under_review",
        submitted_at=datetime.now() - timedelta(days=27),
        estimated_completion=datetime.now() + timedelta(days=3),
    )
    status = get_sla_status(app_obj)
    assert status.status == "at_risk"


def test_get_sla_status_breached():
    app_obj = PermitApplication(
        app_id="PRM-TEST-003",
        applicant_name="Test",
        project_type="residential_construction",
        project_description="Test",
        address="123 Test St",
        status="under_review",
        submitted_at=datetime.now() - timedelta(days=40),
        estimated_completion=datetime.now() - timedelta(days=5),
    )
    status = get_sla_status(app_obj)
    assert status.status == "breached"
    assert status.days_remaining == 0


# --- Endpoint tests ---


def test_status_endpoint():
    resp = client.post(
        "/api/applications/create",
        json={
            "applicant_name": "SLA User",
            "project_type": "commercial_construction",
            "project_description": "Store",
            "address": "100 SLA St",
        },
    )
    assert resp.status_code == 200
    app_id = resp.json()["app_id"]

    resp = client.get(f"/api/applications/{app_id}/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["application_id"] == app_id
    assert data["status"] in ("on_track", "at_risk", "breached")
    assert "days_remaining" in data


def test_status_endpoint_not_found():
    resp = client.get("/api/applications/NONEXISTENT/status")
    assert resp.status_code == 404
