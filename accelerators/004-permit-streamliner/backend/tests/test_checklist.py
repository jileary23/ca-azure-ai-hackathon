"""Tests for document checklist generation service."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.checklist_service import generate_checklist

client = TestClient(app)


# --- Unit tests ---


def test_residential_checklist_items():
    cl = generate_checklist("residential_construction")
    assert len(cl.items) > 0
    names = [item.name for item in cl.items]
    assert "Site plan (to scale)" in names
    assert "Title 24 energy compliance" in names


def test_commercial_checklist_items():
    cl = generate_checklist("commercial_construction")
    names = [item.name for item in cl.items]
    assert "Fire suppression plan" in names
    assert "ADA compliance documentation" in names


def test_demolition_checklist_items():
    cl = generate_checklist("demolition")
    names = [item.name for item in cl.items]
    assert "Asbestos survey" in names
    assert "Lead paint assessment" in names


def test_environmental_checklist_items():
    cl = generate_checklist("environmental_review")
    names = [item.name for item in cl.items]
    assert "Environmental impact report (EIR)" in names


def test_unknown_type_falls_back():
    cl = generate_checklist("unknown_type_xyz")
    assert len(cl.items) > 0


def test_checklist_required_flag():
    cl = generate_checklist("residential_construction")
    required = [i for i in cl.items if i.required]
    optional = [i for i in cl.items if not i.required]
    assert len(required) > 0
    assert len(optional) > 0


def test_coastal_zone_adds_items():
    base = generate_checklist("residential_construction")
    extended = generate_checklist("residential_construction", constraints=["coastal_zone"])
    assert len(extended.items) > len(base.items)
    names = [i.name for i in extended.items]
    assert "Coastal Development Permit application" in names


def test_historic_district_adds_items():
    extended = generate_checklist("residential_construction", constraints=["historic_district"])
    names = [i.name for i in extended.items]
    assert "Historic preservation review application" in names


def test_multiple_constraints():
    extended = generate_checklist(
        "residential_construction",
        constraints=["coastal_zone", "historic_district"],
    )
    names = [i.name for i in extended.items]
    assert "Coastal Development Permit application" in names
    assert "Historic preservation review application" in names


# --- Endpoint tests ---


def test_checklist_endpoint():
    # First create an application
    resp = client.post(
        "/api/applications/create",
        json={
            "applicant_name": "Checklist User",
            "project_type": "commercial_construction",
            "project_description": "Office build-out",
            "address": "500 Commerce Dr",
        },
    )
    assert resp.status_code == 200
    app_id = resp.json()["app_id"]

    # Now get its checklist
    resp = client.get(f"/api/applications/{app_id}/checklist")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert data["items"][0]["name"]


def test_checklist_endpoint_not_found():
    resp = client.get("/api/applications/NONEXISTENT/checklist")
    assert resp.status_code == 404
