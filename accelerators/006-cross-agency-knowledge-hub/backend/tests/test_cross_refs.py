"""Cross-reference service tests — finds pre-defined relationships."""

from app.services import cross_reference_service
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Unit tests ─────────────────────────────────────────────────────────


def test_find_cross_references_existing():
    refs = cross_reference_service.find_cross_references("POL-CDSS-2024-003")
    assert len(refs) > 0
    doc_ids = set()
    for r in refs:
        doc_ids.add(r.source_doc_id)
        doc_ids.add(r.target_doc_id)
    assert "POL-CDSS-2024-003" in doc_ids


def test_find_cross_references_extended():
    refs = cross_reference_service.find_cross_references("POL-CDT-2024-001")
    assert len(refs) > 0
    relationships = [r.relationship for r in refs]
    assert any(r in cross_reference_service.RELATIONSHIP_TYPES for r in relationships)


def test_find_cross_references_none():
    refs = cross_reference_service.find_cross_references("NONEXIST-DOC")
    assert len(refs) == 0


def test_detect_relationship_found():
    rel = cross_reference_service.detect_relationship(
        "POL-CDSS-2024-003", "MEMO-EDD-2024-002"
    )
    assert rel is not None
    assert rel == "complements"


def test_detect_relationship_reverse():
    rel = cross_reference_service.detect_relationship(
        "MEMO-EDD-2024-002", "POL-CDSS-2024-003"
    )
    assert rel is not None


def test_detect_relationship_none():
    rel = cross_reference_service.detect_relationship("DOC-A", "DOC-B")
    assert rel is None


def test_relationship_types_valid():
    refs = cross_reference_service.find_cross_references("POL-CDT-2024-001")
    for r in refs:
        assert r.relationship in cross_reference_service.RELATIONSHIP_TYPES


# ── API endpoint tests ─────────────────────────────────────────────────


def test_api_cross_references():
    response = client.get("/api/cross-references/POL-CDSS-2024-003")
    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == "POL-CDSS-2024-003"
    assert "cross_references" in data
    assert data["total"] > 0


def test_api_cross_references_extended():
    response = client.get("/api/cross-references/POL-CDT-2024-001")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0


def test_api_cross_references_none():
    response = client.get("/api/cross-references/NONEXIST")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
