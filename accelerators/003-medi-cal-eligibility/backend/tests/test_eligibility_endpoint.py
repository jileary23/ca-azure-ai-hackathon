"""Tests for new domain API endpoints via TestClient."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── POST /api/eligibility/screen ──────────────────────────────────────

class TestEligibilityScreenEndpoint:
    def test_eligible_adult(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 1, "monthly_income": 1000, "age": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "eligible_categories" in data
        assert data["fpl_percentage"] > 0
        assert data["magi_income"] == 12_000
        eligible = [c for c in data["eligible_categories"] if c["eligible"]]
        assert len(eligible) >= 1

    def test_ineligible_high_income(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 1, "monthly_income": 8000, "age": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        eligible = [c for c in data["eligible_categories"] if c["eligible"]]
        assert len(eligible) == 0

    def test_family_of_3_2800_monthly(self):
        """Eval scenario: Family of 3, $2800/month, age 35."""
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 3, "monthly_income": 2800, "age": 35,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["magi_income"] == 33_600
        assert data["fpl_percentage"] > 0

    def test_pregnant_individual(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 2, "monthly_income": 2000, "age": 28, "pregnant": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        cats = [c["category"] for c in data["eligible_categories"]]
        assert "pregnant" in cats

    def test_disabled_individual(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 1, "monthly_income": 800, "age": 50, "disabled": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        cats = [c["category"] for c in data["eligible_categories"]]
        assert "disabled" in cats

    def test_child_screening(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 3, "monthly_income": 2000, "age": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        cats = [c["category"] for c in data["eligible_categories"]]
        assert "children_1_5" in cats

    def test_missing_required_field(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 1, "monthly_income": 1000,
        })
        assert resp.status_code == 422  # Missing 'age'

    def test_response_has_next_steps(self):
        resp = client.post("/api/eligibility/screen", json={
            "household_size": 1, "monthly_income": 1000, "age": 30,
        })
        data = resp.json()
        assert len(data["next_steps"]) > 0


# ── POST /api/documents/analyze ───────────────────────────────────────

class TestDocumentAnalyzeEndpoint:
    def test_w2_analysis(self):
        resp = client.post("/api/documents/analyze", json={"document_type": "w2"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_type"] == "w2"
        assert data["confidence"] == 0.95
        assert "wages" in data["extracted_data"]

    def test_pay_stub(self):
        resp = client.post("/api/documents/analyze", json={"document_type": "pay_stub"})
        assert resp.status_code == 200
        assert "gross_pay" in resp.json()["extracted_data"]

    def test_unsupported_document(self):
        resp = client.post("/api/documents/analyze", json={"document_type": "passport"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence"] == 0.0
        assert data["fields_found"] == 0


# ── POST /api/documents/completeness ─────────────────────────────────

class TestDocumentCompletenessEndpoint:
    def test_complete_standard(self):
        resp = client.post("/api/documents/completeness", json={
            "submitted_documents": [
                "photo_id", "proof_of_income", "proof_of_residency", "social_security_card",
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["complete"] is True
        assert data["progress_pct"] == 100.0

    def test_incomplete_standard(self):
        resp = client.post("/api/documents/completeness", json={
            "submitted_documents": ["photo_id"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["complete"] is False
        assert len(data["missing"]) > 0

    def test_pregnancy_application_type(self):
        resp = client.post("/api/documents/completeness", json={
            "submitted_documents": [
                "photo_id", "proof_of_income", "proof_of_residency", "social_security_card",
            ],
            "application_type": "pregnancy",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["complete"] is False


# ── GET /api/eligibility/fpl-guidelines ───────────────────────────────

class TestFPLGuidelinesEndpoint:
    def test_returns_200(self):
        resp = client.get("/api/eligibility/fpl-guidelines")
        assert resp.status_code == 200
        data = resp.json()
        assert data["year"] == 2024
        assert len(data["categories"]) > 0


# ── GET /api/programs ─────────────────────────────────────────────────

class TestListProgramsEndpoint:
    def test_returns_programs(self):
        resp = client.get("/api/programs")
        assert resp.status_code == 200
        programs = resp.json()
        assert len(programs) >= 5

    def test_program_structure(self):
        resp = client.get("/api/programs")
        p = resp.json()[0]
        assert "name" in p
        assert "description" in p
        assert "category" in p
        assert "fpl_threshold" in p
        assert "age_range" in p
        assert "special_requirements" in p


# ── Existing endpoints still work ─────────────────────────────────────

class TestExistingEndpoints:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_status(self):
        resp = client.get("/api/status")
        assert resp.status_code == 200
        assert "agents" in resp.json()

    def test_create_and_get_application(self):
        create_resp = client.post("/api/applications", json={
            "applicant_name": "E2E Test",
            "household_size": 2,
            "monthly_income": 1500,
            "county": "Sacramento",
        })
        assert create_resp.status_code == 200
        app_id = create_resp.json()["app_id"]

        get_resp = client.get(f"/api/applications/{app_id}")
        assert get_resp.status_code == 200
