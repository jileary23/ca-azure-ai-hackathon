"""MAGI income calculation engine for Medi-Cal eligibility screening."""

# 2024 Federal Poverty Level Guidelines (48 contiguous states + DC)
BASE_FPL = 15_060
PER_PERSON_INCREMENT = 5_380

# Medi-Cal FPL thresholds by category (percentage of FPL)
MEDI_CAL_THRESHOLDS: dict[str, int] = {
    "children_0_1": 266,
    "children_1_5": 266,
    "children_6_18": 266,
    "pregnant": 213,
    "adults_19_64": 138,
    "parents_caretakers": 138,
    "aged_65_plus": 138,
    "disabled": 138,
    "former_foster_youth": 266,
}


def calculate_magi(
    agi: float,
    tax_exempt_interest: float = 0,
    foreign_income: float = 0,
    social_security: float = 0,
) -> float:
    """Calculate Modified Adjusted Gross Income.

    MAGI = AGI + tax-exempt interest + foreign income + Social Security benefits.
    """
    return agi + tax_exempt_interest + foreign_income + social_security


def calculate_fpl(household_size: int) -> int:
    """Return the annual Federal Poverty Level for *household_size* (2024)."""
    if household_size < 1:
        household_size = 1
    return BASE_FPL + (household_size - 1) * PER_PERSON_INCREMENT


def calculate_fpl_percentage(household_size: int, annual_income: float) -> float:
    """Return annual income as a percentage of FPL."""
    fpl = calculate_fpl(household_size)
    if fpl == 0:
        return 0.0
    return (annual_income / fpl) * 100


def _applicable_categories(
    age: int,
    pregnant: bool = False,
    disabled: bool = False,
    foster_youth: bool = False,
) -> list[str]:
    """Determine which Medi-Cal categories apply to an individual."""
    categories: list[str] = []

    if foster_youth and age < 26:
        categories.append("former_foster_youth")
    if pregnant:
        categories.append("pregnant")
    if disabled:
        categories.append("disabled")

    if age < 1:
        categories.append("children_0_1")
    elif 1 <= age <= 5:
        categories.append("children_1_5")
    elif 6 <= age <= 18:
        categories.append("children_6_18")
    elif 19 <= age <= 64:
        categories.append("adults_19_64")
        categories.append("parents_caretakers")
    elif age >= 65:
        categories.append("aged_65_plus")

    return categories


def screen_eligibility(
    household_size: int,
    annual_income: float,
    age: int,
    pregnant: bool = False,
    disabled: bool = False,
    foster_youth: bool = False,
) -> dict:
    """Screen eligibility across all applicable Medi-Cal categories.

    Returns a dict with:
        eligible_categories  – list of dicts per qualifying category
        fpl_percentage       – income as %FPL
        household_fpl        – FPL dollar amount for household
        confidence           – screening confidence score
        next_steps           – recommended actions
    """
    fpl = calculate_fpl(household_size)
    fpl_pct = calculate_fpl_percentage(household_size, annual_income)
    categories = _applicable_categories(age, pregnant, disabled, foster_youth)

    eligible_categories: list[dict] = []
    for cat in categories:
        threshold = MEDI_CAL_THRESHOLDS.get(cat, 138)
        income_limit = fpl * (threshold / 100)
        is_eligible = annual_income <= income_limit
        eligible_categories.append(
            {
                "category": cat,
                "threshold_pct": threshold,
                "income_limit": round(income_limit, 2),
                "eligible": is_eligible,
            }
        )

    any_eligible = any(c["eligible"] for c in eligible_categories)

    if any_eligible:
        next_steps = [
            "Complete application at BenefitsCal.com or your county office",
            "Gather required verification documents (ID, income proof, residency)",
            "Submit application — expect a determination within 45 days",
        ]
    else:
        next_steps = [
            "You may qualify for Covered California subsidized health insurance",
            "Check if other household members qualify for Medi-Cal",
            "Visit CoveredCA.com for marketplace options",
        ]

    confidence = 0.95 if categories else 0.70

    return {
        "eligible_categories": eligible_categories,
        "fpl_percentage": round(fpl_pct, 2),
        "household_fpl": fpl,
        "confidence": confidence,
        "next_steps": next_steps,
    }
