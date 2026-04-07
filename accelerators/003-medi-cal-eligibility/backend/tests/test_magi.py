"""Tests for the MAGI income calculation engine."""

import pytest
from app.services.magi_engine import (
    calculate_magi,
    calculate_fpl,
    calculate_fpl_percentage,
    screen_eligibility,
    BASE_FPL,
    PER_PERSON_INCREMENT,
    MEDI_CAL_THRESHOLDS,
    _applicable_categories,
)


# ── calculate_magi ────────────────────────────────────────────────────

class TestCalculateMAGI:
    def test_agi_only(self):
        assert calculate_magi(50_000) == 50_000

    def test_all_components(self):
        result = calculate_magi(40_000, tax_exempt_interest=500, foreign_income=1_000, social_security=2_000)
        assert result == 43_500

    def test_zero_agi(self):
        assert calculate_magi(0, social_security=1_200) == 1_200

    def test_negative_agi(self):
        # Losses can produce negative AGI
        assert calculate_magi(-5_000, tax_exempt_interest=200) == -4_800


# ── calculate_fpl ─────────────────────────────────────────────────────

class TestCalculateFPL:
    def test_individual(self):
        assert calculate_fpl(1) == BASE_FPL

    def test_household_of_2(self):
        assert calculate_fpl(2) == BASE_FPL + PER_PERSON_INCREMENT

    def test_household_of_4(self):
        assert calculate_fpl(4) == BASE_FPL + 3 * PER_PERSON_INCREMENT

    def test_household_of_8(self):
        assert calculate_fpl(8) == BASE_FPL + 7 * PER_PERSON_INCREMENT

    def test_zero_defaults_to_one(self):
        assert calculate_fpl(0) == BASE_FPL

    def test_negative_defaults_to_one(self):
        assert calculate_fpl(-3) == BASE_FPL

    def test_increments_linearly(self):
        for size in range(2, 9):
            assert calculate_fpl(size) - calculate_fpl(size - 1) == PER_PERSON_INCREMENT


# ── calculate_fpl_percentage ──────────────────────────────────────────

class TestCalculateFPLPercentage:
    def test_at_fpl(self):
        pct = calculate_fpl_percentage(1, float(BASE_FPL))
        assert abs(pct - 100.0) < 0.01

    def test_double_fpl(self):
        pct = calculate_fpl_percentage(1, float(BASE_FPL * 2))
        assert abs(pct - 200.0) < 0.01

    def test_zero_income(self):
        assert calculate_fpl_percentage(1, 0) == 0.0


# ── screen_eligibility ───────────────────────────────────────────────

class TestScreenEligibility:
    def test_low_income_adult(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=30)
        cats = [c for c in result["eligible_categories"] if c["eligible"]]
        assert len(cats) >= 1
        assert result["confidence"] == 0.95

    def test_high_income_adult_not_eligible(self):
        result = screen_eligibility(household_size=1, annual_income=100_000, age=30)
        eligible = [c for c in result["eligible_categories"] if c["eligible"]]
        assert len(eligible) == 0

    def test_child_under_1(self):
        result = screen_eligibility(household_size=2, annual_income=30_000, age=0)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "children_0_1" in categories

    def test_child_1_to_5(self):
        result = screen_eligibility(household_size=3, annual_income=20_000, age=3)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "children_1_5" in categories

    def test_child_6_to_18(self):
        result = screen_eligibility(household_size=3, annual_income=20_000, age=10)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "children_6_18" in categories

    def test_pregnant_individual(self):
        result = screen_eligibility(household_size=2, annual_income=20_000, age=28, pregnant=True)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "pregnant" in categories

    def test_disabled_individual(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=45, disabled=True)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "disabled" in categories

    def test_aged_65_plus(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=70)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "aged_65_plus" in categories

    def test_foster_youth(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=22, foster_youth=True)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "former_foster_youth" in categories

    def test_foster_youth_over_26_not_applicable(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=30, foster_youth=True)
        categories = [c["category"] for c in result["eligible_categories"]]
        assert "former_foster_youth" not in categories

    def test_fpl_percentage_present(self):
        result = screen_eligibility(household_size=1, annual_income=15_060, age=30)
        assert abs(result["fpl_percentage"] - 100.0) < 0.01

    def test_next_steps_for_eligible(self):
        result = screen_eligibility(household_size=1, annual_income=10_000, age=30)
        assert any("BenefitsCal" in s for s in result["next_steps"])

    def test_next_steps_for_ineligible(self):
        result = screen_eligibility(household_size=1, annual_income=200_000, age=30)
        assert any("Covered California" in s for s in result["next_steps"])

    def test_household_fpl_returned(self):
        result = screen_eligibility(household_size=3, annual_income=20_000, age=30)
        assert result["household_fpl"] == calculate_fpl(3)
