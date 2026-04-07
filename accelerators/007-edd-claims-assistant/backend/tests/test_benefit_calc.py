"""Tests for benefit_calculator service."""

from app.services.benefit_calculator import (
    calculate_ui_benefit,
    calculate_di_benefit,
    calculate_pfl_benefit,
    UI_MIN_WBA,
    UI_MAX_WBA,
    DI_MIN_WBA,
    DI_MAX_WBA,
    PFL_MAX_WEEKS,
)


class TestUIBenefit:
    def test_basic_calculation(self):
        result = calculate_ui_benefit([12000.0, 8000.0, 9000.0, 10000.0])
        assert result["claim_type"] == "UI"
        # highest quarter = 12000, WBA = 12000/26 ≈ 461.54 → capped at 450
        assert result["weekly_benefit"] == UI_MAX_WBA
        assert result["max_weeks"] == 26
        assert result["total_benefit"] == UI_MAX_WBA * 26

    def test_minimum_cap(self):
        # Very low earnings: WBA = 500/26 ≈ 19.23 → floor at $40
        result = calculate_ui_benefit([500.0])
        assert result["weekly_benefit"] == UI_MIN_WBA

    def test_maximum_cap(self):
        result = calculate_ui_benefit([50000.0])
        assert result["weekly_benefit"] == UI_MAX_WBA

    def test_mid_range(self):
        # highest = 5200, WBA = 5200/26 = 200.0
        result = calculate_ui_benefit([5200.0, 3000.0])
        assert result["weekly_benefit"] == 200.0
        assert result["total_benefit"] == 200.0 * 26

    def test_zero_earnings(self):
        result = calculate_ui_benefit([0.0])
        assert result["weekly_benefit"] == 0.0

    def test_empty_earnings(self):
        result = calculate_ui_benefit([])
        assert result["weekly_benefit"] == 0.0

    def test_base_period_earnings_sum(self):
        result = calculate_ui_benefit([1000.0, 2000.0, 3000.0])
        assert result["base_period_earnings"] == 6000.0


class TestDIBenefit:
    def test_high_income_60_percent(self):
        # highest = 10000 (>$5500 threshold), rate = 60%
        # WBA = (10000/13) * 0.60 ≈ 461.54
        result = calculate_di_benefit([10000.0, 8000.0])
        assert result["claim_type"] == "DI"
        assert result["replacement_rate"] == 0.60
        assert result["weekly_benefit"] == round((10000 / 13) * 0.60, 2)

    def test_low_income_70_percent(self):
        # highest = 4000 (<$5500), rate = 70%
        # WBA = (4000/13) * 0.70 ≈ 215.38
        result = calculate_di_benefit([4000.0])
        assert result["replacement_rate"] == 0.70
        assert result["weekly_benefit"] == round((4000 / 13) * 0.70, 2)

    def test_minimum_cap(self):
        # Very low: highest = 500, WBA = (500/13)*0.70 ≈ 26.92 → floor $50
        result = calculate_di_benefit([500.0])
        assert result["weekly_benefit"] == DI_MIN_WBA

    def test_maximum_cap(self):
        result = calculate_di_benefit([100000.0])
        assert result["weekly_benefit"] == DI_MAX_WBA

    def test_zero_earnings(self):
        result = calculate_di_benefit([0.0])
        assert result["weekly_benefit"] == 0.0

    def test_max_weeks_52(self):
        result = calculate_di_benefit([10000.0])
        assert result["max_weeks"] == 52


class TestPFLBenefit:
    def test_same_formula_as_di(self):
        di = calculate_di_benefit([8000.0])
        pfl = calculate_pfl_benefit([8000.0])
        assert pfl["weekly_benefit"] == di["weekly_benefit"]
        assert pfl["replacement_rate"] == di["replacement_rate"]

    def test_max_weeks_8(self):
        result = calculate_pfl_benefit([8000.0])
        assert result["max_weeks"] == PFL_MAX_WEEKS

    def test_total_benefit(self):
        result = calculate_pfl_benefit([8000.0])
        assert result["total_benefit"] == round(result["weekly_benefit"] * PFL_MAX_WEEKS, 2)

    def test_claim_type_label(self):
        result = calculate_pfl_benefit([5000.0])
        assert result["claim_type"] == "PFL"
