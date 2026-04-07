"""Tests for FPL calculation and pre-screening logic."""

import pytest

from app.services.fpl_service import (
    BASE_FPL,
    PER_PERSON_INCREMENT,
    calculate_fpl,
    calculate_fpl_percentage,
    prescreen_eligibility,
)


# --- FPL calculation ---


def test_fpl_single_person():
    assert calculate_fpl(1) == BASE_FPL  # $15,060


def test_fpl_two_person():
    assert calculate_fpl(2) == BASE_FPL + PER_PERSON_INCREMENT  # $20,440


def test_fpl_four_person():
    assert calculate_fpl(4) == BASE_FPL + 3 * PER_PERSON_INCREMENT  # $31,200


def test_fpl_eight_person():
    assert calculate_fpl(8) == BASE_FPL + 7 * PER_PERSON_INCREMENT  # $52,720


def test_fpl_invalid_household_size():
    with pytest.raises(ValueError):
        calculate_fpl(0)


# --- FPL percentage ---


def test_fpl_percentage_at_100():
    fpl = calculate_fpl(1)
    pct = calculate_fpl_percentage(1, float(fpl))
    assert pct == pytest.approx(100.0)


def test_fpl_percentage_at_200():
    fpl = calculate_fpl(4)
    pct = calculate_fpl_percentage(4, float(fpl * 2))
    assert pct == pytest.approx(200.0)


def test_fpl_percentage_partial():
    pct = calculate_fpl_percentage(1, 7_530.0)
    assert pct == pytest.approx(50.0)


# --- Pre-screening ---


def test_prescreen_under_limits():
    """Family of 4 earning $1,500/mo should be eligible for most programs."""
    results = prescreen_eligibility(4, 1_500.0)
    assert len(results) >= 5
    for r in results:
        assert r["likely_eligible"] is True
        assert r["fpl_percentage"] < 100


def test_prescreen_over_limits():
    """Single person earning $10,000/mo should exceed all thresholds."""
    results = prescreen_eligibility(1, 10_000.0)
    for r in results:
        assert r["likely_eligible"] is False


def test_prescreen_specific_programs():
    """Filter to only CalFresh and Medi-Cal."""
    results = prescreen_eligibility(2, 2_000.0, programs=["calfresh", "medi_cal"])
    programs = {r["program"] for r in results}
    assert programs == {"calfresh", "medi_cal"}


def test_prescreen_result_structure():
    results = prescreen_eligibility(1, 1_000.0)
    for r in results:
        assert "program" in r
        assert "likely_eligible" in r
        assert "fpl_percentage" in r
        assert "threshold" in r
        assert "confidence" in r
        assert "factors" in r
        assert "next_steps" in r
        assert isinstance(r["factors"], list)
        assert isinstance(r["next_steps"], list)


def test_prescreen_near_boundary():
    """Income near the FPL boundary should have lower confidence."""
    fpl = calculate_fpl(1)
    # Just over 100% FPL — near the CAPI/GR thresholds
    monthly = (fpl * 1.02) / 12
    results = prescreen_eligibility(1, monthly, programs=["capi"])
    assert len(results) == 1
    assert results[0]["confidence"] <= 0.85  # near-boundary
