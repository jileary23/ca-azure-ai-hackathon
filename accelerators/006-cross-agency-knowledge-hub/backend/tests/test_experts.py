"""Expert service tests — topic search returns relevant experts."""

from app.services import expert_service
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Unit tests ─────────────────────────────────────────────────────────


def test_find_experts_by_topic():
    experts = expert_service.find_experts("AI governance")
    assert len(experts) > 0
    areas = []
    for e in experts:
        areas.extend(e.expertise_areas)
    area_text = " ".join(areas).lower()
    assert "ai" in area_text or "governance" in area_text


def test_find_experts_by_agency():
    experts = expert_service.find_experts("policy", agency="CDT")
    assert len(experts) > 0
    for e in experts:
        assert e.agency == "CDT"


def test_find_experts_procurement():
    experts = expert_service.find_experts("procurement")
    assert len(experts) > 0
    names = [e.name for e in experts]
    assert any("Patel" in n or "Brown" in n for n in names)


def test_find_experts_medi_cal():
    experts = expert_service.find_experts("Medi-Cal")
    assert len(experts) > 0
    agencies = {e.agency for e in experts}
    assert "DHCS" in agencies


def test_find_experts_no_match():
    experts = expert_service.find_experts("xyzzynotreal", agency="NONEXIST")
    assert len(experts) == 0


def test_get_expert_found():
    expert = expert_service.get_expert("EXP-001")
    assert expert is not None
    assert expert.expert_id == "EXP-001"
    assert expert.name == "Maria Chen"


def test_get_expert_extended():
    expert = expert_service.get_expert("EXP-007")
    assert expert is not None
    assert expert.agency == "CDT"


def test_get_expert_not_found():
    expert = expert_service.get_expert("EXP-999")
    assert expert is None


# ── API endpoint tests ─────────────────────────────────────────────────


def test_api_experts_by_topic():
    response = client.get("/api/experts?topic=data+privacy")
    assert response.status_code == 200
    data = response.json()
    assert "experts" in data
    assert data["total"] > 0


def test_api_experts_by_agency():
    response = client.get("/api/experts?topic=policy&agency=CDT")
    assert response.status_code == 200
    data = response.json()
    for e in data["experts"]:
        assert e["agency"] == "CDT"


def test_api_expert_detail():
    response = client.get("/api/experts/EXP-001")
    assert response.status_code == 200
    data = response.json()
    assert data["expert_id"] == "EXP-001"
    assert "expertise_areas" in data


def test_api_expert_not_found():
    response = client.get("/api/experts/EXP-999")
    assert response.status_code == 404
    assert response.json()["error"] == "Expert not found"
