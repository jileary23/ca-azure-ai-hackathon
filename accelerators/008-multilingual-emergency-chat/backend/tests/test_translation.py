"""Tests for /api/translate endpoint and translation service."""


def test_translate_text(client):
    resp = client.post(
        "/api/translate",
        json={"text": "Fire warning", "target_lang": "es"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["translated_text"] == "Fire warning [es]"
    assert data["source_lang"] == "en"
    assert data["target_lang"] == "es"


def test_translate_same_language(client):
    resp = client.post(
        "/api/translate",
        json={"text": "Hello", "target_lang": "en", "source_lang": "en"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["translated_text"] == "Hello"


def test_translate_missing_fields(client):
    resp = client.post("/api/translate", json={"text": "Hello"})
    assert resp.status_code == 422  # target_lang required


def test_status_shows_supported_languages(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    langs = data["supported_languages"]
    assert "en" in langs
    assert "es" in langs
    assert "zh-Hans" in langs
    assert "vi" in langs
    assert len(langs) >= 15


def test_status_shows_new_endpoints(client):
    resp = client.get("/api/status")
    data = resp.json()
    assert "/api/alerts" in data["endpoints"]
    assert "/api/shelters" in data["endpoints"]
    assert "/api/air-quality" in data["endpoints"]
    assert "/api/translate" in data["endpoints"]
