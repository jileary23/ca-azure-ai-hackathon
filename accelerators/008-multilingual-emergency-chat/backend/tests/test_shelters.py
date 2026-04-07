"""Tests for /api/shelters endpoint."""


def test_find_shelters_by_zip(client):
    resp = client.get("/api/shelters", params={"zip": "95814"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    shelter = data[0]
    assert "id" in shelter
    assert "name" in shelter
    assert "address" in shelter
    assert "capacity" in shelter
    assert isinstance(shelter["services"], list)
    assert isinstance(shelter["accepts_pets"], bool)
    assert isinstance(shelter["ada_accessible"], bool)


def test_find_shelters_returns_distance(client):
    resp = client.get("/api/shelters", params={"zip": "95814"})
    assert resp.status_code == 200
    data = resp.json()
    for shelter in data:
        assert "distance_miles" in shelter
        assert shelter["distance_miles"] is not None


def test_find_shelters_unknown_zip_returns_all(client):
    resp = client.get("/api/shelters", params={"zip": "00000", "radius": 5})
    assert resp.status_code == 200
    data = resp.json()
    # Unknown ZIP still returns results (fallback: all shelters sorted by distance)
    assert isinstance(data, list)
    assert len(data) >= 1


def test_find_shelters_missing_zip(client):
    resp = client.get("/api/shelters")
    assert resp.status_code == 422  # zip is required


def test_find_shelters_custom_radius(client):
    resp = client.get("/api/shelters", params={"zip": "90210", "radius": 50})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
