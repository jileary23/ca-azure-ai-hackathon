"""Fee estimation service for permit applications."""

from app.models.schemas import FeeEstimate
from app.services.intake_service import PERMIT_TYPES


def estimate_fees(
    project_type: str,
    project_value: float = 0,
    expedited: bool = False,
    constraints: list[str] | None = None,
) -> FeeEstimate:
    """Estimate permit fees for a project.

    Modifiers:
    - project_value > $500k: +50% plan review surcharge
    - environmental constraint: +$1000 CEQA fee
    - coastal_zone constraint: +$500 coastal commission fee
    - expedited flag: +100% rush fee
    """
    info = PERMIT_TYPES.get(project_type, PERMIT_TYPES["residential_construction"])
    base_fee = float(info["fee_base"])
    modifiers: list[dict] = []
    total = base_fee

    if project_value > 500_000:
        surcharge = base_fee * 0.50
        modifiers.append({
            "name": "Plan review surcharge (project > $500k)",
            "amount": surcharge,
        })
        total += surcharge

    constraints = constraints or []
    if "environmental_review" in constraints:
        modifiers.append({"name": "CEQA review fee", "amount": 1000.0})
        total += 1000.0

    if "coastal_zone" in constraints:
        modifiers.append({"name": "Coastal commission fee", "amount": 500.0})
        total += 500.0

    if expedited:
        rush = total  # 100% of current total
        modifiers.append({"name": "Expedited processing (100%)", "amount": rush})
        total += rush

    breakdown = {
        "base_fee": base_fee,
        "modifiers": {m["name"]: m["amount"] for m in modifiers},
        "total": round(total, 2),
    }

    return FeeEstimate(
        base_fee=base_fee,
        modifiers=modifiers,
        total_fee=round(total, 2),
        breakdown=breakdown,
    )
