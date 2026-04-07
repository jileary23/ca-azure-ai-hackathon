"""Tests for county office lookup endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_offices_all():
    resp = client.get("/api/offices")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 8


def test_offices_filter_by_county():
    resp = client.get("/api/offices", params={"county": "Sacramento"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    for office in data:
        assert office["county"] == "Sacramento"


def test_offices_filter_case_insensitive():
    resp = client.get("/api/offices", params={"county": "los angeles"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["county"] == "Los Angeles"


def test_offices_unknown_county():
    resp = client.get("/api/offices", params={"county": "Atlantis"})
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_office_structure():
    resp = client.get("/api/offices")
    data = resp.json()
    office = data[0]
    assert "name" in office
    assert "county" in office
    assert "address" in office
    assert "phone" in office
    assert "hours" in office
    assert "languages_served" in office
    assert "services" in office
    assert isinstance(office["languages_served"], list)
    assert isinstance(office["services"], list)


def test_office_has_services():
    """Every office should offer at least one service."""
    resp = client.get("/api/offices")
    for office in resp.json():
        assert len(office["services"]) >= 1
