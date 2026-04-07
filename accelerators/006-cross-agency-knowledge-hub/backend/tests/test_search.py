"""Search service tests — keyword match, agency filter, permission filtering."""

from fastapi.testclient import TestClient
from app.main import app
from app.services import search_service, permission_service

client = TestClient(app)


# ── Unit tests for search_service ──────────────────────────────────────


def test_search_keyword_match():
    results = search_service.search("AI governance policy")
    assert len(results) > 0
    titles = [r.title for r in results]
    assert any("AI" in t for t in titles)


def test_search_returns_sorted_by_relevance():
    results = search_service.search("Medi-Cal eligibility")
    assert len(results) >= 2
    scores = [r.relevance_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_agency_filter():
    results = search_service.search("policy", agencies=["CDSS"])
    assert len(results) > 0
    for r in results:
        assert r.agency == "CDSS"


def test_search_doc_type_filter():
    results = search_service.search("guidance", doc_types=["guidance"])
    assert len(results) > 0
    for r in results:
        assert r.document_type == "guidance"


def test_search_permission_filter():
    public_agencies = permission_service.get_accessible_agencies("public")
    results = search_service.search("policy", user_permissions=public_agencies)
    for r in results:
        assert r.agency in public_agencies


def test_search_limit():
    results = search_service.search("policy", limit=3)
    assert len(results) <= 3


def test_search_no_match_returns_empty_or_low():
    results = search_service.search("xyzzyzxnotarealquery", agencies=["NONEXIST"])
    assert len(results) == 0


def test_get_document_detail_found():
    detail = search_service.get_document_detail("POL-CDT-2024-001")
    assert detail is not None
    assert detail["doc_id"] == "POL-CDT-2024-001"
    assert "cross_references" in detail


def test_get_document_detail_not_found():
    detail = search_service.get_document_detail("DOES-NOT-EXIST")
    assert detail is None


# ── API endpoint tests ─────────────────────────────────────────────────


def test_api_search_basic():
    response = client.get("/api/search?query=policy")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert data["total"] > 0


def test_api_search_with_agency():
    response = client.get("/api/search?query=policy&agency=CDSS")
    assert response.status_code == 200
    data = response.json()
    for doc in data["results"]:
        assert doc["agency"] == "CDSS"


def test_api_search_with_role():
    response = client.get("/api/search?query=policy&role=public")
    assert response.status_code == 200
    data = response.json()
    public_agencies = permission_service.get_accessible_agencies("public")
    for doc in data["results"]:
        assert doc["agency"] in public_agencies


def test_api_search_state_employee_sees_more():
    resp_public = client.get("/api/search?query=benefits&role=public")
    resp_emp = client.get("/api/search?query=benefits&role=state_employee")
    assert resp_public.status_code == 200
    assert resp_emp.status_code == 200
    assert resp_emp.json()["total"] >= resp_public.json()["total"]


def test_api_document_found():
    response = client.get("/api/documents/POL-CDT-2024-001")
    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == "POL-CDT-2024-001"
    assert "cross_references" in data


def test_api_document_without_refs():
    response = client.get("/api/documents/POL-CDT-2024-001?include_refs=false")
    assert response.status_code == 200
    data = response.json()
    assert "cross_references" not in data


def test_api_document_not_found():
    response = client.get("/api/documents/NONEXIST")
    assert response.status_code == 404
    assert response.json()["error"] == "Document not found"
