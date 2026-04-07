"""Agency-scoped access control service (mock Entra ID)."""

AGENCY_PERMISSIONS: dict[str, list[str]] = {
    "public": ["CDT", "GovOps", "OPR"],
    "state_employee": [
        "CDT", "GovOps", "OPR", "CDSS", "DHCS", "EDD", "DGS", "HCD", "DCA",
        "CalHR", "Caltrans",
    ],
    "admin": ["all"],
}

AGENCY_DIRECTORY: dict[str, str] = {
    "CDT": "California Department of Technology",
    "GovOps": "Government Operations Agency",
    "OPR": "Governor's Office of Planning and Research",
    "CDSS": "California Department of Social Services",
    "DHCS": "Department of Health Care Services",
    "EDD": "Employment Development Department",
    "DGS": "Department of General Services",
    "HCD": "Department of Housing and Community Development",
    "DCA": "Department of Consumer Affairs",
    "CalHR": "California Department of Human Resources",
    "Caltrans": "California Department of Transportation",
}


def check_permission(user_role: str, agency: str) -> bool:
    """Check if user role has access to agency documents."""
    allowed = AGENCY_PERMISSIONS.get(user_role)
    if allowed is None:
        return False
    if "all" in allowed:
        return True
    return agency in allowed


def get_accessible_agencies(user_role: str) -> list[str]:
    """List agencies accessible to this user role."""
    allowed = AGENCY_PERMISSIONS.get(user_role)
    if allowed is None:
        return []
    if "all" in allowed:
        return list(AGENCY_DIRECTORY.keys())
    return [a for a in allowed if a in AGENCY_DIRECTORY]


def get_agency_info(user_role: str) -> list[dict]:
    """Return agency code + name for accessible agencies."""
    codes = get_accessible_agencies(user_role)
    return [
        {"agency_code": code, "agency_name": AGENCY_DIRECTORY[code]}
        for code in codes
    ]
