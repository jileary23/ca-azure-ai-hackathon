"""Tests for eligibility_service."""

from app.services.eligibility_service import (
    screen_ui_eligibility,
    screen_di_eligibility,
    screen_pfl_eligibility,
)


class TestScreenUIEligibility:
    def test_eligible_layoff(self):
        result = screen_ui_eligibility({
            "quarterly_earnings": [5000.0, 4000.0, 3000.0, 2000.0],
            "separation_reason": "layoff",
            "able_to_work": True,
            "available_for_work": True,
        })
        assert result.likely_eligible is True
        assert result.confidence >= 0.8
        assert result.claim_type == "UI"

    def test_insufficient_wages(self):
        result = screen_ui_eligibility({
            "quarterly_earnings": [500.0, 200.0],
            "separation_reason": "layoff",
            "able_to_work": True,
            "available_for_work": True,
        })
        assert result.likely_eligible is False

    def test_voluntary_quit(self):
        result = screen_ui_eligibility({
            "quarterly_earnings": [5000.0, 4000.0],
            "separation_reason": "quit",
            "able_to_work": True,
            "available_for_work": True,
        })
        assert result.likely_eligible is False

    def test_not_available_for_work(self):
        result = screen_ui_eligibility({
            "quarterly_earnings": [5000.0],
            "separation_reason": "layoff",
            "able_to_work": True,
            "available_for_work": False,
        })
        assert result.likely_eligible is False

    def test_alt_wage_rule(self):
        # $900 in highest + total >= 1.25 * highest
        result = screen_ui_eligibility({
            "quarterly_earnings": [1000.0, 300.0],
            "separation_reason": "layoff",
            "able_to_work": True,
            "available_for_work": True,
        })
        # 1000 >= 900 and 1300 >= 1.25*1000 = 1250 → True
        assert result.likely_eligible is True

    def test_empty_earnings(self):
        result = screen_ui_eligibility({
            "quarterly_earnings": [],
            "separation_reason": "layoff",
            "able_to_work": True,
            "available_for_work": True,
        })
        assert result.likely_eligible is False


class TestScreenDIEligibility:
    def test_eligible(self):
        result = screen_di_eligibility(
            employment_status="employed",
            medical_condition=True,
            base_period_earnings=5000.0,
        )
        assert result.likely_eligible is True
        assert result.claim_type == "DI"

    def test_not_employed(self):
        result = screen_di_eligibility(
            employment_status="unemployed",
            medical_condition=True,
            base_period_earnings=5000.0,
        )
        assert result.likely_eligible is False

    def test_no_medical_condition(self):
        result = screen_di_eligibility(
            employment_status="employed",
            medical_condition=False,
            base_period_earnings=5000.0,
        )
        assert result.likely_eligible is False

    def test_insufficient_earnings(self):
        result = screen_di_eligibility(
            employment_status="employed",
            medical_condition=True,
            base_period_earnings=100.0,
        )
        assert result.likely_eligible is False


class TestScreenPFLEligibility:
    def test_eligible_bonding(self):
        result = screen_pfl_eligibility(
            reason="bonding",
            employment_status="employed",
            base_period_earnings=5000.0,
        )
        assert result.likely_eligible is True
        assert result.claim_type == "PFL"

    def test_eligible_care(self):
        result = screen_pfl_eligibility(
            reason="care",
            employment_status="employed",
            base_period_earnings=500.0,
        )
        assert result.likely_eligible is True

    def test_invalid_reason(self):
        result = screen_pfl_eligibility(
            reason="vacation",
            employment_status="employed",
            base_period_earnings=5000.0,
        )
        assert result.likely_eligible is False

    def test_insufficient_earnings(self):
        result = screen_pfl_eligibility(
            reason="bonding",
            employment_status="employed",
            base_period_earnings=100.0,
        )
        assert result.likely_eligible is False
