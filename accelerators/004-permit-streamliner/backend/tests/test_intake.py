"""Tests for intake classification service."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.intake_service import classify_project, create_application, PERMIT_TYPES

client = TestClient(app)


# --- Unit tests ---


def test_classify_residential():
    result = classify_project("I want to build an addition to my house")
    assert result["project_type"] == "residential_construction"
    assert result["agency"] == "HCD"
    assert result["confidence"] >= 0.5


def test_classify_commercial():
    result = classify_project("New retail store and office building")
    assert result["project_type"] == "commercial_construction"
    assert result["agency"] == "HCD"


def test_classify_environmental():
    result = classify_project("Environmental impact review for wetland project")
    assert result["project_type"] == "environmental_review"
    assert result["agency"] == "OPR"
    assert result["estimated_sla_days"] == 60


def test_classify_demolition():
    result = classify_project("I need to demolish an old building and tear down the structure")
    assert result["project_type"] == "demolition"
    assert result["agency"] == "HCD"


def test_classify_business_license():
    result = classify_project("I want to open a business and need a business license")
    assert result["project_type"] == "business_license"
    assert result["agency"] == "DCA"


def test_classify_electrical():
    result = classify_project("Need to upgrade electrical panel and wiring")
    assert result["project_type"] == "electrical"
    assert result["estimated_fees"] == 150.0


def test_classify_unknown_defaults_to_residential():
    result = classify_project("xyz abc unknown gibberish")
    assert result["project_type"] == "residential_construction"
    assert result["confidence"] == 0.3


def test_classify_returns_all_fields():
    result = classify_project("Build a new home")
    assert "project_type" in result
    assert "agency" in result
    assert "estimated_sla_days" in result
    assert "estimated_fees" in result
    assert "confidence" in result


def test_create_application():
    app_obj = create_application(
        project_type="residential_construction",
        description="New house",
        address="100 Test St",
        applicant="Jane Doe",
    )
    assert app_obj.app_id.startswith("PRM-")
    assert app_obj.status == "submitted"
    assert app_obj.applicant_name == "Jane Doe"
    assert app_obj.submitted_at is not None
    assert app_obj.estimated_completion is not None


def test_create_application_unknown_type_defaults():
    app_obj = create_application(
        project_type="unknown_type",
        description="Something",
        address="999 Nowhere",
        applicant="Test",
    )
    assert app_obj.status == "submitted"


# --- Endpoint tests ---


def test_classify_endpoint():
    resp = client.post(
        "/api/intake/classify",
        json={"description": "I want to build a residential addition in Sacramento"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_type"] == "residential_construction"
    assert data["agency"] == "HCD"
    assert "estimated_sla_days" in data
    assert "estimated_fees" in data


def test_classify_endpoint_commercial():
    resp = client.post(
        "/api/intake/classify",
        json={"description": "Opening a new retail store downtown"},
    )
    assert resp.status_code == 200
    assert resp.json()["project_type"] == "commercial_construction"


def test_create_application_endpoint():
    resp = client.post(
        "/api/applications/create",
        json={
            "applicant_name": "Test User",
            "project_type": "residential_construction",
            "project_description": "Build a house",
            "address": "123 Test Ave",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["app_id"].startswith("PRM-")
    assert data["status"] == "submitted"
    assert data["applicant_name"] == "Test User"
