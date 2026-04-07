"""Public Safety Power Shutoff status for Wildfire Response Coordinator."""

from datetime import datetime, timedelta, timezone

UTILITIES = {
    "pge": {"name": "Pacific Gas & Electric", "service_area": "Northern/Central CA"},
    "sce": {"name": "Southern California Edison", "service_area": "Southern CA (excl. LA/SD)"},
    "sdge": {"name": "San Diego Gas & Electric", "service_area": "San Diego County"},
}

_MOCK_PSPS: dict[str, dict] = {
    "pge": {
        "utility_code": "pge",
        "utility_name": "Pacific Gas & Electric",
        "status": "active",
        "affected_areas": ["Butte County", "Plumas County", "Shasta County", "Tehama County"],
        "estimated_restoration": (datetime.now(timezone.utc) + timedelta(hours=36)).isoformat(),
    },
    "sce": {
        "utility_code": "sce",
        "utility_name": "Southern California Edison",
        "status": "planned",
        "affected_areas": ["Ventura County", "Santa Barbara County"],
        "estimated_restoration": (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat(),
    },
    "sdge": {
        "utility_code": "sdge",
        "utility_name": "San Diego Gas & Electric",
        "status": "none",
        "affected_areas": [],
        "estimated_restoration": None,
    },
}


def get_psps_status(utility: str | None = None) -> list[dict]:
    """Get PSPS status for utilities."""
    if utility:
        key = utility.lower()
        entry = _MOCK_PSPS.get(key)
        if entry is None:
            return []
        return [dict(entry)]
    return [dict(v) for v in _MOCK_PSPS.values()]


def get_affected_areas(utility: str) -> list[str]:
    """Get list of areas affected by PSPS."""
    key = utility.lower()
    entry = _MOCK_PSPS.get(key)
    if entry is None:
        return []
    return list(entry["affected_areas"])
