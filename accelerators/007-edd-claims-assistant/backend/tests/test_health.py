"""Health check and API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "edd-claims-assistant"
    assert "mock_mode" in data


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "EDD Claims Assistant"
    assert "supported_claim_types" in data
    assert "UI" in data["supported_claim_types"]


def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "Check my unemployment claim status"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "citations" in data
    assert data["confidence"] > 0


def test_chat_with_claim_type():
    response = client.post(
        "/api/chat",
        json={"message": "Am I eligible for disability insurance?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0


def test_claim_status_endpoint():
    response = client.post(
        "/api/claim-status",
        json={"claim_type": "UI", "last_four_ssn": "1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert "status" in data


def test_eligibility_endpoint():
    response = client.post(
        "/api/eligibility",
        json={"claim_type": "UI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert "likely_eligible" in data
    assert "requirements" in data


def test_document_checklist_endpoint():
    response = client.post(
        "/api/document-checklist",
        json={"claim_type": "UI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "required" in data[0]


# ── New domain endpoint tests ────────────────────────────────────────────────


def test_calculate_benefits_ui():
    response = client.post(
        "/api/benefits/calculate",
        json={"claim_type": "UI", "quarterly_earnings": [12000.0, 8000.0, 9000.0, 10000.0]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert data["weekly_benefit"] == 450.0
    assert data["max_weeks"] == 26


def test_calculate_benefits_di():
    response = client.post(
        "/api/benefits/calculate",
        json={"claim_type": "DI", "quarterly_earnings": [10000.0]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "DI"
    assert data["max_weeks"] == 52


def test_calculate_benefits_pfl():
    response = client.post(
        "/api/benefits/calculate",
        json={"claim_type": "PFL", "quarterly_earnings": [8000.0]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "PFL"
    assert data["max_weeks"] == 8


def test_calculate_benefits_invalid_type():
    response = client.post(
        "/api/benefits/calculate",
        json={"claim_type": "XYZ", "quarterly_earnings": [5000.0]},
    )
    assert response.status_code == 400


def test_claim_timeline_ui():
    response = client.get("/api/claims/ui/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert data["estimated_days"] == 21
    assert len(data["steps"]) > 0


def test_claim_timeline_di():
    response = client.get("/api/claims/di/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_days"] == 14


def test_claim_timeline_invalid():
    response = client.get("/api/claims/xyz/timeline")
    assert response.status_code == 404


def test_claim_requirements_ui():
    response = client.get("/api/claims/ui/requirements")
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "UI"
    assert len(data["eligibility_requirements"]) > 0
    assert len(data["required_documents"]) > 0


def test_claim_requirements_pfl():
    response = client.get("/api/claims/pfl/requirements")
    assert response.status_code == 200
    data = response.json()
    assert data["claim_type"] == "PFL"


def test_claim_requirements_invalid():
    response = client.get("/api/claims/xyz/requirements")
    assert response.status_code == 404


def test_escalate_endpoint():
    response = client.post(
        "/api/escalate",
        json={"reason": "My claim was denied and I want to appeal", "claim_type": "UI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"].startswith("TKT-")
    assert data["priority"] in ("urgent", "high", "medium")
    assert "estimated_wait" in data
    assert data["queue_position"] >= 1


def test_escalate_fraud():
    response = client.post(
        "/api/escalate",
        json={"reason": "Someone committed fraud on my account"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "urgent"
