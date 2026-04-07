"""Benefit amount calculator for UI, DI, and PFL programs."""

# 2024 California EDD benefit rates
UI_MIN_WBA = 40.0
UI_MAX_WBA = 450.0
UI_MAX_WEEKS = 26

DI_MIN_WBA = 50.0
DI_MAX_WBA = 1620.0
DI_MAX_WEEKS = 52

PFL_MIN_WBA = 50.0
PFL_MAX_WBA = 1620.0
PFL_MAX_WEEKS = 8

# Approx 1/3 of CA state average quarterly wage (2024)
CA_STATE_AVG_QUARTER_THIRD = 5_500.0


def _highest_quarter(quarterly_earnings: list[float]) -> float:
    if not quarterly_earnings:
        return 0.0
    return max(quarterly_earnings)


def calculate_ui_benefit(quarterly_earnings: list[float]) -> dict:
    """Calculate UI weekly benefit amount.

    WBA = highest quarter earnings / 26, clamped to [$40, $450].
    Maximum duration is 26 weeks.
    """
    highest = _highest_quarter(quarterly_earnings)
    wba = highest / 26.0 if highest > 0 else 0.0
    wba = max(UI_MIN_WBA, min(UI_MAX_WBA, round(wba, 2)))
    if highest == 0:
        wba = 0.0
    return {
        "claim_type": "UI",
        "weekly_benefit": wba,
        "max_weeks": UI_MAX_WEEKS,
        "total_benefit": round(wba * UI_MAX_WEEKS, 2),
        "replacement_rate": round(wba * 26 / highest, 4) if highest > 0 else 0.0,
        "base_period_earnings": round(sum(quarterly_earnings), 2),
    }


def calculate_di_benefit(quarterly_earnings: list[float]) -> dict:
    """Calculate DI weekly benefit amount.

    Replacement rate is 70% if highest quarter < 1/3 state avg, else 60%.
    WBA = (highest quarter / 13) * replacement_rate, clamped to [$50, $1620].
    Maximum duration is 52 weeks.
    """
    highest = _highest_quarter(quarterly_earnings)
    if highest == 0:
        return {
            "claim_type": "DI",
            "weekly_benefit": 0.0,
            "max_weeks": DI_MAX_WEEKS,
            "total_benefit": 0.0,
            "replacement_rate": 0.0,
            "base_period_earnings": 0.0,
        }

    replacement_rate = 0.70 if highest < CA_STATE_AVG_QUARTER_THIRD else 0.60
    wba = (highest / 13.0) * replacement_rate
    wba = max(DI_MIN_WBA, min(DI_MAX_WBA, round(wba, 2)))
    return {
        "claim_type": "DI",
        "weekly_benefit": wba,
        "max_weeks": DI_MAX_WEEKS,
        "total_benefit": round(wba * DI_MAX_WEEKS, 2),
        "replacement_rate": replacement_rate,
        "base_period_earnings": round(sum(quarterly_earnings), 2),
    }


def calculate_pfl_benefit(quarterly_earnings: list[float]) -> dict:
    """Calculate PFL weekly benefit amount.

    Same formula as DI but maximum duration is 8 weeks.
    """
    result = calculate_di_benefit(quarterly_earnings)
    result["claim_type"] = "PFL"
    result["max_weeks"] = PFL_MAX_WEEKS
    result["total_benefit"] = round(result["weekly_benefit"] * PFL_MAX_WEEKS, 2)
    return result
