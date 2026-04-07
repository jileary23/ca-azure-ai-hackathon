"""Tests for /api/air-quality endpoint."""


def test_get_aqi(client):
    resp = client.get("/api/air-quality", params={"zip": "95814"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["zip_code"] == "95814"
    assert isinstance(data["aqi"], int)
    assert data["aqi"] > 0
    assert data["category"] in (
        "Good",
        "Moderate",
        "Unhealthy for Sensitive Groups",
        "Unhealthy",
        "Very Unhealthy",
        "Hazardous",
    )
    assert "dominant_pollutant" in data
    assert "health_guidance" in data
    assert "updated_at" in data


def test_get_aqi_unknown_zip(client):
    resp = client.get("/api/air-quality", params={"zip": "00000"})
    assert resp.status_code == 200
    data = resp.json()
    # Falls back to default AQI
    assert data["zip_code"] == "00000"
    assert isinstance(data["aqi"], int)


def test_get_aqi_missing_zip(client):
    resp = client.get("/api/air-quality")
    assert resp.status_code == 422  # zip is required


def test_aqi_known_zip_values(client):
    """Sacramento (95814) should be unhealthy for sensitive groups (AQI 142)."""
    resp = client.get("/api/air-quality", params={"zip": "95814"})
    data = resp.json()
    assert data["aqi"] == 142
    assert data["category"] == "Unhealthy for Sensitive Groups"
