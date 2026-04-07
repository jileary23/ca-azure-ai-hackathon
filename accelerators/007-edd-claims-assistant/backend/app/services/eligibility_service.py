"""Eligibility pre-screening for UI, DI, and PFL programs."""

from __future__ import annotations

from app.models.schemas import EligibilityAssessment

# CA 2024 eligibility thresholds
UI_MIN_HIGHEST_QUARTER = 1300.0
UI_ALT_HIGHEST_QUARTER = 900.0


def screen_ui_eligibility(employment_history: dict) -> EligibilityAssessment:
    """Screen for UI eligibility based on employment history.

    ``employment_history`` should include:
    - quarterly_earnings: list[float] — earnings for each quarter of the base period
    - separation_reason: str — e.g. "layoff", "quit", "fired"
    - able_to_work: bool
    - available_for_work: bool
    """
    quarterly = employment_history.get("quarterly_earnings", [])
    separation = employment_history.get("separation_reason", "").lower()
    able = employment_history.get("able_to_work", True)
    available = employment_history.get("available_for_work", True)

    highest = max(quarterly) if quarterly else 0.0
    total = sum(quarterly)

    factors: list[str] = []
    requirements_met: list[str] = []
    requirements_unmet: list[str] = []

    # Wage check: $1,300 in highest quarter OR $900 + total >= 1.25 * highest
    wages_ok = highest >= UI_MIN_HIGHEST_QUARTER or (
        highest >= UI_ALT_HIGHEST_QUARTER and total >= 1.25 * highest
    )
    if wages_ok:
        requirements_met.append("Earned sufficient wages in base period")
    else:
        requirements_unmet.append(
            f"Insufficient base period wages (highest quarter: ${highest:,.2f})"
        )

    # Separation reason
    involuntary = separation in ("layoff", "laid off", "reduction in force", "rif", "company closure")
    if involuntary:
        requirements_met.append("Lost job through no fault of own")
    elif separation:
        requirements_unmet.append(f"Separation reason '{separation}' may not qualify")
    else:
        factors.append("Separation reason not provided — cannot fully assess")

    # Able and available
    if able and available:
        requirements_met.append("Able and available to work")
    else:
        requirements_unmet.append("Must be able and available to work")

    eligible = wages_ok and involuntary and able and available
    confidence = 0.90 if eligible and not factors else 0.60 if eligible else 0.40

    next_steps = []
    if eligible:
        next_steps = [
            "File your claim online at edd.ca.gov",
            "Gather your last employer's information",
            "Register with CalJOBS (caljobs.ca.gov)",
        ]
    else:
        next_steps = [
            "Review EDD eligibility requirements at edd.ca.gov",
            "Consider filing anyway — EDD makes the final determination",
            "Contact EDD at 1-800-300-5616 for personalized help",
        ]

    return EligibilityAssessment(
        claim_type="UI",
        likely_eligible=eligible,
        confidence=confidence,
        factors=factors + requirements_met + requirements_unmet,
        requirements=requirements_met,
        next_steps=next_steps,
    )


def screen_di_eligibility(
    employment_status: str,
    medical_condition: bool,
    base_period_earnings: float = 0.0,
) -> EligibilityAssessment:
    """Screen for DI eligibility.

    Requirements:
    - Employed or recently self-employed with SDI coverage
    - Earned >= $300 in base period
    - Has a medical condition preventing work
    - Under doctor's care
    """
    factors: list[str] = []
    requirements_met: list[str] = []
    requirements_unmet: list[str] = []

    employed = employment_status.lower() in ("employed", "self-employed", "self_employed")
    if employed:
        requirements_met.append("Currently employed or self-employed with SDI coverage")
    else:
        requirements_unmet.append("Must be employed or self-employed with SDI coverage")

    if base_period_earnings >= 300:
        requirements_met.append(f"Earned ${base_period_earnings:,.2f} in base period (min $300)")
    else:
        requirements_unmet.append(
            f"Base period earnings ${base_period_earnings:,.2f} below $300 minimum"
        )

    if medical_condition:
        requirements_met.append("Has a medical condition preventing work")
    else:
        requirements_unmet.append("Must have a medical condition that prevents work")

    factors.append("Must be under care and treatment of a licensed physician")

    eligible = employed and base_period_earnings >= 300 and medical_condition
    confidence = 0.85 if eligible else 0.35

    next_steps = (
        [
            "Obtain physician's certification of disability",
            "File your DI claim online at edd.ca.gov",
            "Submit medical records from treating physician",
        ]
        if eligible
        else [
            "Consult with your physician about your condition",
            "Review DI eligibility at edd.ca.gov",
            "Contact EDD at 1-800-480-3287 for assistance",
        ]
    )

    return EligibilityAssessment(
        claim_type="DI",
        likely_eligible=eligible,
        confidence=confidence,
        factors=factors + requirements_met + requirements_unmet,
        requirements=requirements_met,
        next_steps=next_steps,
    )


def screen_pfl_eligibility(
    reason: str,
    employment_status: str,
    base_period_earnings: float = 0.0,
) -> EligibilityAssessment:
    """Screen for PFL eligibility.

    Requirements:
    - Qualifying reason: bonding, care, or military assist
    - Earned >= $300 in base period
    - Employment with SDI contributions
    """
    factors: list[str] = []
    requirements_met: list[str] = []
    requirements_unmet: list[str] = []

    qualifying_reasons = {"bonding", "care", "caring", "military assist", "military_assist"}
    reason_ok = reason.lower().replace("-", " ").replace("_", " ") in qualifying_reasons
    if reason_ok:
        requirements_met.append(f"Qualifying reason: {reason}")
    else:
        requirements_unmet.append(
            f"Reason '{reason}' may not be a qualifying PFL reason (bonding, care, or military assist)"
        )

    employed = employment_status.lower() in ("employed", "self-employed", "self_employed")
    if employed:
        requirements_met.append("Currently employed with SDI contributions")
    else:
        requirements_unmet.append("Must be employed with SDI contributions")

    if base_period_earnings >= 300:
        requirements_met.append(f"Earned ${base_period_earnings:,.2f} in base period (min $300)")
    else:
        requirements_unmet.append(
            f"Base period earnings ${base_period_earnings:,.2f} below $300 minimum"
        )

    eligible = reason_ok and employed and base_period_earnings >= 300
    confidence = 0.85 if eligible else 0.35

    next_steps = (
        [
            "Notify your employer of your intent to take PFL",
            "File your PFL claim online at edd.ca.gov",
            "Provide required certification documentation",
        ]
        if eligible
        else [
            "Review PFL qualifying reasons at edd.ca.gov",
            "Contact EDD at 1-877-238-4373 for assistance",
        ]
    )

    return EligibilityAssessment(
        claim_type="PFL",
        likely_eligible=eligible,
        confidence=confidence,
        factors=factors + requirements_met + requirements_unmet,
        requirements=requirements_met,
        next_steps=next_steps,
    )
