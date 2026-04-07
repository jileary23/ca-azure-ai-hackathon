"""Tests for eligibility pre-screening endpoint and program requirements."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# --- POST /api/eligibility/prescreen ---


def test_prescreen_basic():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={"household_size": 4, "monthly_income": 2500.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["household_size"] == 4
    assert data["monthly_income"] == 2500.0
    assert data["annual_income"] == 30_000.0
    assert "fpl_amount" in data
    assert "fpl_percentage" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) >= 1


def test_prescreen_response_structure():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={"household_size": 1, "monthly_income": 1000.0},
    )
    data = resp.json()
    for r in data["results"]:
        assert "program" in r
        assert "likely_eligible" in r
        assert "fpl_percentage" in r
        assert "threshold" in r
        assert "confidence" in r
        assert "factors" in r
        assert "next_steps" in r


def test_prescreen_with_county():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={"household_size": 2, "monthly_income": 1500.0, "county": "Sacramento"},
    )
    assert resp.status_code == 200


def test_prescreen_specific_programs():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={
            "household_size": 3,
            "monthly_income": 2000.0,
            "programs": ["calfresh", "medi_cal"],
        },
    )
    data = resp.json()
    programs = {r["program"] for r in data["results"]}
    assert programs == {"calfresh", "medi_cal"}


def test_prescreen_zero_income():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={"household_size": 1, "monthly_income": 0.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["fpl_percentage"] == 0.0
    for r in data["results"]:
        assert r["likely_eligible"] is True


def test_prescreen_negative_income():
    resp = client.post(
        "/api/eligibility/prescreen",
        json={"household_size": 1, "monthly_income": -100.0},
    )
    assert resp.status_code == 422


# --- GET /api/programs/{program_id}/requirements ---


def test_program_requirements_calfresh():
    resp = client.get("/api/programs/calfresh/requirements")
    assert resp.status_code == 200
    data = resp.json()
    assert data["program_id"] == "calfresh"
    assert "requirements" in data
    assert "documents_needed" in data
    assert "income_limits" in data
    assert "policy_ref" in data


def test_program_requirements_calworks():
    resp = client.get("/api/programs/calworks/requirements")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "CalWORKs"


def test_program_requirements_not_found():
    resp = client.get("/api/programs/nonexistent/requirements")
    assert resp.status_code == 404


# --- GET /api/languages ---


def test_languages_endpoint():
    resp = client.get("/api/languages")
    assert resp.status_code == 200
    data = resp.json()
    codes = [lang["code"] for lang in data]
    assert "en" in codes
    assert "es" in codes
    assert "zh" in codes
    assert len(data) >= 8
