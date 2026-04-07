"""Permit intake classification service."""

import re
import uuid
from datetime import datetime, timedelta

from app.models.schemas import PermitApplication

PERMIT_TYPES: dict[str, dict] = {
    "residential_construction": {"agency": "HCD", "base_sla_days": 30, "fee_base": 500},
    "commercial_construction": {"agency": "HCD", "base_sla_days": 45, "fee_base": 1500},
    "business_license": {"agency": "DCA", "base_sla_days": 15, "fee_base": 200},
    "professional_license": {"agency": "DCA", "base_sla_days": 20, "fee_base": 300},
    "environmental_review": {"agency": "OPR", "base_sla_days": 60, "fee_base": 2000},
    "demolition": {"agency": "HCD", "base_sla_days": 20, "fee_base": 400},
    "grading": {"agency": "HCD", "base_sla_days": 25, "fee_base": 600},
    "electrical": {"agency": "HCD", "base_sla_days": 10, "fee_base": 150},
    "plumbing": {"agency": "HCD", "base_sla_days": 10, "fee_base": 150},
    "mechanical": {"agency": "HCD", "base_sla_days": 10, "fee_base": 150},
}

_KEYWORDS: dict[str, list[str]] = {
    "residential_construction": [
        "house", "home", "residence", "residential", "addition", "adu",
        "accessory dwelling", "room", "garage", "remodel", "renovation",
        "kitchen", "bedroom", "bathroom", "deck", "patio",
    ],
    "commercial_construction": [
        "commercial", "office", "retail", "store", "restaurant", "warehouse",
        "shop", "mall", "hotel", "mixed-use", "mixed use",
    ],
    "business_license": [
        "business license", "operate", "open a business", "business permit",
        "start a business",
    ],
    "professional_license": [
        "professional license", "contractor license", "medical license",
        "engineering license", "professional",
    ],
    "environmental_review": [
        "environmental", "ceqa", "eir", "environmental impact",
        "environmental review", "habitat", "wetland",
    ],
    "demolition": ["demolition", "demolish", "tear down", "remove structure"],
    "grading": ["grading", "excavation", "earthwork", "site grading", "land grading"],
    "electrical": ["electrical", "wiring", "panel", "circuit", "solar panel"],
    "plumbing": ["plumbing", "pipe", "sewer", "water line", "drain"],
    "mechanical": ["mechanical", "hvac", "heating", "cooling", "ventilation"],
}

# Pre-compile word-boundary patterns for single-word keywords
_COMPILED: dict[str, list[tuple[re.Pattern, int]]] = {}
for _ptype, _kws in _KEYWORDS.items():
    patterns = []
    for kw in _kws:
        # Multi-word phrases use substring match; single words use word boundary
        if " " in kw:
            patterns.append((re.compile(re.escape(kw)), 1))
        else:
            patterns.append((re.compile(rf"\b{re.escape(kw)}\b"), 1))
    _COMPILED[_ptype] = patterns


def classify_project(description: str) -> dict:
    """Classify project type based on description keywords."""
    lower = description.lower()
    scores: dict[str, int] = {}
    for ptype, patterns in _COMPILED.items():
        score = sum(w for pat, w in patterns if pat.search(lower))
        if score > 0:
            scores[ptype] = score

    if not scores:
        best = "residential_construction"
        confidence = 0.3
    else:
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        confidence = min(0.95, 0.5 + 0.1 * scores[best])

    info = PERMIT_TYPES[best]
    return {
        "project_type": best,
        "agency": info["agency"],
        "estimated_sla_days": info["base_sla_days"],
        "estimated_fees": float(info["fee_base"]),
        "confidence": round(confidence, 2),
    }


def create_application(
    project_type: str,
    description: str,
    address: str,
    applicant: str,
    project_value: float = 0,
) -> PermitApplication:
    """Create a new permit application with a generated ID."""
    app_id = f"PRM-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:5].upper()}"
    info = PERMIT_TYPES.get(project_type, PERMIT_TYPES["residential_construction"])
    sla_days = info["base_sla_days"]

    return PermitApplication(
        app_id=app_id,
        applicant_name=applicant,
        project_type=project_type,
        project_description=description,
        address=address,
        status="submitted",
        submitted_at=datetime.now(),
        estimated_completion=datetime.now() + timedelta(days=sla_days),
    )
