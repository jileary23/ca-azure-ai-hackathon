"""2024 Federal Poverty Level calculator for benefits eligibility screening."""

# 2024 FPL Guidelines (48 contiguous states + DC)
BASE_FPL = 15_060  # 1-person household
PER_PERSON_INCREMENT = 5_380

# Program income thresholds as percentage of FPL
PROGRAM_THRESHOLDS: dict[str, dict] = {
    "calfresh": {"max_fpl_pct": 200, "gross_income": True},
    "calworks": {"max_fpl_pct": 130, "net_income": True},
    "medi_cal": {"max_fpl_pct": 138, "magi_based": True},
    "capi": {"max_fpl_pct": 100, "ssi_linked": True},
    "general_relief": {"max_fpl_pct": 100, "county_specific": True},
}


def calculate_fpl(household_size: int) -> int:
    """Return annual FPL dollar amount for the given household size."""
    if household_size < 1:
        raise ValueError("Household size must be at least 1")
    return BASE_FPL + (household_size - 1) * PER_PERSON_INCREMENT


def calculate_fpl_percentage(household_size: int, annual_income: float) -> float:
    """Return income as a percentage of FPL for the given household size."""
    fpl = calculate_fpl(household_size)
    return (annual_income / fpl) * 100


def prescreen_eligibility(
    household_size: int,
    monthly_income: float,
    programs: list[str] | None = None,
) -> list[dict]:
    """Pre-screen eligibility for one or more benefit programs.

    Returns a list of dicts, one per program, with eligibility assessment.
    """
    annual_income = monthly_income * 12
    fpl = calculate_fpl(household_size)
    fpl_pct = calculate_fpl_percentage(household_size, annual_income)

    target_programs = programs or list(PROGRAM_THRESHOLDS.keys())
    results: list[dict] = []

    for prog_id in target_programs:
        threshold = PROGRAM_THRESHOLDS.get(prog_id)
        if threshold is None:
            continue

        max_pct = threshold["max_fpl_pct"]
        likely_eligible = fpl_pct <= max_pct

        # Build contextual factors
        factors: list[str] = [
            f"Household income is {fpl_pct:.0f}% of FPL",
            f"Program threshold is {max_pct}% of FPL",
        ]
        if threshold.get("gross_income"):
            factors.append("Based on gross income test")
        if threshold.get("net_income"):
            factors.append("Based on net income test")
        if threshold.get("magi_based"):
            factors.append("Uses Modified Adjusted Gross Income (MAGI)")
        if threshold.get("ssi_linked"):
            factors.append("Linked to SSI eligibility criteria")
        if threshold.get("county_specific"):
            factors.append("Exact limits vary by county")

        # Confidence based on how close to threshold
        distance = abs(fpl_pct - max_pct)
        if distance > 30:
            confidence = 0.95
        elif distance > 10:
            confidence = 0.85
        else:
            confidence = 0.70  # near the boundary

        next_steps: list[str] = []
        if likely_eligible:
            next_steps = [
                "Apply online at BenefitsCal.com",
                "Gather required documents",
                "Schedule an eligibility interview",
            ]
        else:
            next_steps = [
                "Review other assistance programs",
                "Contact your county office for a detailed review",
                "Income changes may affect future eligibility",
            ]

        results.append(
            {
                "program": prog_id,
                "likely_eligible": likely_eligible,
                "fpl_percentage": round(fpl_pct, 1),
                "threshold": float(max_pct),
                "confidence": confidence,
                "factors": factors,
                "next_steps": next_steps,
            }
        )

    return results
