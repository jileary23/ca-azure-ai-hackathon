"""Incident lifecycle management for Wildfire Response Coordinator."""

import uuid
from datetime import datetime, timezone

_incidents: dict[str, dict] = {}

INCIDENT_TYPES = {
    "wildfire": {"lead_agency": "CAL FIRE", "priority": "critical"},
    "earthquake": {"lead_agency": "Cal OES", "priority": "critical"},
    "flood": {"lead_agency": "DWR", "priority": "high"},
    "hazmat": {"lead_agency": "CHP", "priority": "high"},
    "tsunami": {"lead_agency": "Cal OES", "priority": "critical"},
    "landslide": {"lead_agency": "Caltrans", "priority": "high"},
    "power_outage": {"lead_agency": "CPUC", "priority": "medium"},
}

_seq = 0


def _next_id() -> str:
    global _seq
    _seq += 1
    year = datetime.now(timezone.utc).year
    return f"INC-{year}-{_seq:03d}"


def _seed_incidents() -> None:
    """Pre-seed demo incidents."""
    if _incidents:
        return
    now = datetime.now(timezone.utc).isoformat()
    seeds = [
        {
            "incident_type": "wildfire",
            "name": "Paradise Ridge Fire",
            "location": "Paradise Ridge, Butte County",
            "description": "Fast-moving wildfire in steep terrain with limited access",
            "severity": "critical",
        },
        {
            "incident_type": "wildfire",
            "name": "Topanga Canyon Fire",
            "location": "Topanga Canyon, Los Angeles County",
            "description": "Brush fire threatening residential structures in canyon",
            "severity": "high",
        },
        {
            "incident_type": "flood",
            "name": "American River Flood",
            "location": "American River Parkway, Sacramento",
            "description": "River flooding along parkway after atmospheric river event",
            "severity": "high",
        },
        {
            "incident_type": "earthquake",
            "name": "Hayward Fault Tremor",
            "location": "Hayward, Alameda County",
            "description": "4.2 magnitude earthquake along Hayward Fault",
            "severity": "medium",
        },
    ]
    for s in seeds:
        create_incident(
            incident_type=s["incident_type"],
            name=s["name"],
            location=s["location"],
            description=s["description"],
            severity=s["severity"],
        )


def create_incident(
    incident_type: str,
    name: str,
    location: str,
    description: str,
    severity: str = "high",
) -> dict:
    """Create a new incident report."""
    incident_id = _next_id()
    type_info = INCIDENT_TYPES.get(incident_type, {"lead_agency": "Cal OES", "priority": "high"})
    now = datetime.now(timezone.utc).isoformat()

    incident = {
        "incident_id": incident_id,
        "incident_type": incident_type,
        "name": name,
        "location": location,
        "description": description,
        "severity": severity,
        "status": "active",
        "lead_agency": type_info["lead_agency"],
        "created_at": now,
        "updated_at": now,
        "resources": [],
    }
    _incidents[incident_id] = incident
    return incident


def get_incident(incident_id: str) -> dict | None:
    """Get incident details."""
    _seed_incidents()
    return _incidents.get(incident_id)


def update_incident(incident_id: str, updates: dict) -> dict | None:
    """Update incident status/details."""
    _seed_incidents()
    incident = _incidents.get(incident_id)
    if incident is None:
        return None
    allowed = {"status", "severity", "description", "name", "location"}
    for key, value in updates.items():
        if key in allowed:
            incident[key] = value
    incident["updated_at"] = datetime.now(timezone.utc).isoformat()
    return incident


def list_incidents(status: str | None = None, incident_type: str | None = None) -> list[dict]:
    """List incidents, optionally filtered."""
    _seed_incidents()
    results = list(_incidents.values())
    if status:
        results = [i for i in results if i["status"] == status]
    if incident_type:
        results = [i for i in results if i["incident_type"] == incident_type]
    return results


def reset() -> None:
    """Reset state — for testing."""
    global _seq
    _incidents.clear()
    _seq = 0
