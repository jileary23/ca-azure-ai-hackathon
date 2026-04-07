"""Tests for fee estimation service."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.fee_service import estimate_fees

client = TestClient(app)


# --- Unit tests ---


def test_base_fee_residential():
    result = estimate_fees("residential_construction")
    assert result.base_fee == 500.0
    assert result.total_fee == 500.0
    assert result.modifiers == []


def test_base_fee_commercial():
    result = estimate_fees("commercial_construction")
    assert result.base_fee == 1500.0
    assert result.total_fee == 1500.0


def test_base_fee_environmental():
    result = estimate_fees("environmental_review")
    assert result.base_fee == 2000.0


def test_high_value_surcharge():
    result = estimate_fees("residential_construction", project_value=600_000)
    assert result.total_fee == 500.0 + 250.0  # +50% surcharge
    assert len(result.modifiers) == 1
    assert result.modifiers[0]["amount"] == 250.0


def test_no_surcharge_under_500k():
    result = estimate_fees("residential_construction", project_value=499_999)
    assert result.total_fee == 500.0
    assert len(result.modifiers) == 0


def test_environmental_constraint_fee():
    result = estimate_fees("residential_construction", constraints=["environmental_review"])
    assert result.total_fee == 500.0 + 1000.0
    mod_names = [m["name"] for m in result.modifiers]
    assert "CEQA review fee" in mod_names


def test_coastal_constraint_fee():
    result = estimate_fees("residential_construction", constraints=["coastal_zone"])
    assert result.total_fee == 500.0 + 500.0
    mod_names = [m["name"] for m in result.modifiers]
    assert "Coastal commission fee" in mod_names


def test_expedited_doubles():
    result = estimate_fees("residential_construction", expedited=True)
    assert result.total_fee == 500.0 * 2  # base + 100% rush
    mod_names = [m["name"] for m in result.modifiers]
    assert any("Expedited" in n for n in mod_names)


def test_all_modifiers_combined():
    result = estimate_fees(
        "residential_construction",
        project_value=1_000_000,
        expedited=True,
        constraints=["environmental_review", "coastal_zone"],
    )
    # base=500, surcharge=250, ceqa=1000, coastal=500, subtotal=2250, rush=2250
    expected = (500 + 250 + 1000 + 500) * 2
    assert result.total_fee == expected


def test_fee_breakdown_present():
    result = estimate_fees("commercial_construction", project_value=700_000)
    assert "base_fee" in result.breakdown
    assert "total" in result.breakdown


def test_unknown_type_defaults():
    result = estimate_fees("unknown_xyz")
    assert result.base_fee == 500.0  # defaults to residential


# --- Endpoint tests ---


def test_fee_estimate_endpoint_basic():
    resp = client.post(
        "/api/fees/estimate",
        json={"project_type": "commercial_construction"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["base_fee"] == 1500.0
    assert data["total_fee"] == 1500.0


def test_fee_estimate_endpoint_with_modifiers():
    resp = client.post(
        "/api/fees/estimate",
        json={
            "project_type": "residential_construction",
            "project_value": 800_000,
            "expedited": True,
            "constraints": ["coastal_zone"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_fee"] > data["base_fee"]
    assert len(data["modifiers"]) > 0


def test_fee_estimate_endpoint_environmental():
    resp = client.post(
        "/api/fees/estimate",
        json={
            "project_type": "environmental_review",
            "project_value": 0,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["base_fee"] == 2000.0
