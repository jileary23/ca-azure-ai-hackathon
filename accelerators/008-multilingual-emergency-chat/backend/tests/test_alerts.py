"""Tests for /api/alerts endpoint."""

import pytest


def test_get_all_alerts(client):
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    for alert in data:
        assert "id" in alert
        assert alert["type"] in ("fire", "earthquake", "flood", "tsunami")
        assert alert["severity"] in ("extreme", "severe", "moderate", "minor")
        assert isinstance(alert["areas_affected"], list)


def test_get_alerts_by_zip(client):
    resp = client.get("/api/alerts", params={"zip": "90210"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for alert in data:
        assert "90210" in alert["areas_affected"]


def test_get_alerts_by_zip_no_results(client):
    resp = client.get("/api/alerts", params={"zip": "00000"})
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_get_alerts_translated(client):
    resp = client.get("/api/alerts", params={"lang": "es"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    # Mock translation appends [es]
    assert "[es]" in data[0]["headline"]
    assert "[es]" in data[0]["description"]


def test_get_alerts_english_no_suffix(client):
    resp = client.get("/api/alerts", params={"lang": "en"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert "[en]" not in data[0]["headline"]
