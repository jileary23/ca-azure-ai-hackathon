"""FPL service with Medi-Cal-specific thresholds and income limits."""

from app.services.magi_engine import (
    BASE_FPL,
    PER_PERSON_INCREMENT,
    MEDI_CAL_THRESHOLDS,
    calculate_fpl,
)

# Human-readable labels for each threshold category
CATEGORY_LABELS: dict[str, str] = {
    "children_0_1": "Children under 1",
    "children_1_5": "Children 1–5",
    "children_6_18": "Children 6–18",
    "pregnant": "Pregnant individuals",
    "adults_19_64": "Adults 19–64 (ACA expansion)",
    "parents_caretakers": "Parent/caretaker relatives",
    "aged_65_plus": "Aged 65+",
    "disabled": "Disabled individuals",
    "former_foster_youth": "Former foster youth under 26",
}


def get_fpl_guidelines() -> dict:
    """Return current FPL guidelines with Medi-Cal income thresholds.

    Includes income limits for household sizes 1–8 across every category.
    """
    categories: list[dict] = []
    for cat, threshold_pct in MEDI_CAL_THRESHOLDS.items():
        limits_by_household: dict[int, float] = {}
        for size in range(1, 9):
            fpl = calculate_fpl(size)
            limits_by_household[size] = round(fpl * (threshold_pct / 100), 2)

        categories.append(
            {
                "category": cat,
                "label": CATEGORY_LABELS.get(cat, cat),
                "fpl_threshold_pct": threshold_pct,
                "income_limits_by_household_size": limits_by_household,
            }
        )

    return {
        "year": 2024,
        "base_fpl": BASE_FPL,
        "per_person_increment": PER_PERSON_INCREMENT,
        "categories": categories,
    }


def get_income_limit(category: str, household_size: int) -> float:
    """Return the annual income limit for a category and household size.

    Raises ValueError if the category is unknown.
    """
    threshold_pct = MEDI_CAL_THRESHOLDS.get(category)
    if threshold_pct is None:
        raise ValueError(f"Unknown category: {category}")
    fpl = calculate_fpl(household_size)
    return round(fpl * (threshold_pct / 100), 2)
