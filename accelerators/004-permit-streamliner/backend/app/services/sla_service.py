"""SLA tracking service for permit applications."""

from datetime import datetime, timedelta

from app.models.schemas import PermitApplication, SLAStatus
from app.services.intake_service import PERMIT_TYPES

CONSTRAINT_MODIFIERS: dict[str, int] = {
    "environmental_review": 15,
    "coastal_zone": 10,
    "historic_district": 20,
    "multi_agency": 10,
}


def calculate_sla(project_type: str, constraints: list[str] | None = None) -> int:
    """Calculate total SLA days for a project type with optional constraints."""
    info = PERMIT_TYPES.get(project_type, PERMIT_TYPES["residential_construction"])
    base_days = info["base_sla_days"]

    extra = sum(
        CONSTRAINT_MODIFIERS.get(c, 0) for c in (constraints or [])
    )
    return base_days + extra


def get_sla_status(application: PermitApplication) -> SLAStatus:
    """Compute live SLA status for an application."""
    info = PERMIT_TYPES.get(
        application.project_type, PERMIT_TYPES["residential_construction"]
    )
    agency = info["agency"]

    assigned = application.submitted_at or datetime.now()
    due = application.estimated_completion or (
        assigned + timedelta(days=info["base_sla_days"])
    )

    now = datetime.now()
    remaining = (due - now).days

    if remaining < 0:
        status = "breached"
    elif remaining <= 5:
        status = "at_risk"
    else:
        status = "on_track"

    return SLAStatus(
        application_id=application.app_id,
        department=agency,
        assigned_date=assigned,
        due_date=due,
        status=status,
        days_remaining=max(remaining, 0),
    )
