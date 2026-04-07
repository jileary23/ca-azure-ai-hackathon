"""Dynamic document checklist generation service."""

from app.models.schemas import ChecklistItem, DocumentChecklist

_BASE_CHECKLISTS: dict[str, list[dict]] = {
    "residential_construction": [
        {"name": "Site plan (to scale)", "required": True},
        {"name": "Floor plan with dimensions", "required": True},
        {"name": "Title 24 energy compliance", "required": True},
        {"name": "Structural calculations", "required": True},
        {"name": "Proof of ownership", "required": True},
        {"name": "CEQA exemption form", "required": False},
    ],
    "commercial_construction": [
        {"name": "Architectural plans", "required": True},
        {"name": "Structural engineering plans", "required": True},
        {"name": "Fire suppression plan", "required": True},
        {"name": "ADA compliance documentation", "required": True},
        {"name": "Health department approval", "required": True},
        {"name": "Parking analysis", "required": True},
        {"name": "CEQA clearance", "required": True},
    ],
    "business_license": [
        {"name": "Business plan summary", "required": True},
        {"name": "Proof of identity", "required": True},
        {"name": "Lease or property deed", "required": True},
        {"name": "Zoning verification letter", "required": True},
        {"name": "Fire clearance certificate", "required": False},
    ],
    "professional_license": [
        {"name": "Professional credentials", "required": True},
        {"name": "Proof of identity", "required": True},
        {"name": "Education transcripts", "required": True},
        {"name": "Examination results", "required": True},
        {"name": "Background check authorization", "required": True},
    ],
    "environmental_review": [
        {"name": "Project description and scope", "required": True},
        {"name": "Initial study checklist", "required": True},
        {"name": "Environmental impact report (EIR)", "required": True},
        {"name": "Biological resources assessment", "required": True},
        {"name": "Cultural resources survey", "required": True},
        {"name": "Traffic impact study", "required": False},
        {"name": "Air quality analysis", "required": False},
        {"name": "Noise study", "required": False},
    ],
    "demolition": [
        {"name": "Demolition plan", "required": True},
        {"name": "Asbestos survey", "required": True},
        {"name": "Lead paint assessment", "required": True},
        {"name": "Utility disconnect confirmation", "required": True},
        {"name": "Site restoration plan", "required": False},
    ],
    "grading": [
        {"name": "Grading plan (engineered)", "required": True},
        {"name": "Soils/geotechnical report", "required": True},
        {"name": "Erosion control plan", "required": True},
        {"name": "Drainage study", "required": True},
        {"name": "SWPPP (Stormwater Pollution Prevention Plan)", "required": False},
    ],
    "electrical": [
        {"name": "Electrical plan", "required": True},
        {"name": "Load calculations", "required": True},
        {"name": "Panel schedule", "required": True},
        {"name": "Solar system specifications", "required": False},
    ],
    "plumbing": [
        {"name": "Plumbing plan", "required": True},
        {"name": "Isometric diagram", "required": True},
        {"name": "Fixture schedule", "required": True},
        {"name": "Water heater specifications", "required": False},
    ],
    "mechanical": [
        {"name": "Mechanical plan", "required": True},
        {"name": "HVAC load calculations", "required": True},
        {"name": "Equipment specifications", "required": True},
        {"name": "Duct layout", "required": True},
        {"name": "Energy compliance forms", "required": False},
    ],
}

_ZONE_EXTRA_ITEMS: dict[str, list[dict]] = {
    "coastal_zone": [
        {"name": "Coastal Development Permit application", "required": True},
        {"name": "Coastal Commission review form", "required": True},
    ],
    "historic_district": [
        {"name": "Historic preservation review application", "required": True},
        {"name": "Secretary of Interior standards compliance", "required": True},
    ],
    "flood_zone": [
        {"name": "Flood elevation certificate", "required": True},
        {"name": "Floodplain development permit", "required": True},
    ],
    "fire_zone": [
        {"name": "Wildfire risk assessment", "required": True},
        {"name": "Defensible space compliance plan", "required": True},
    ],
}


def generate_checklist(
    project_type: str,
    address: str | None = None,
    constraints: list[str] | None = None,
) -> DocumentChecklist:
    """Generate a document checklist for the given project type.

    Args:
        project_type: One of the PERMIT_TYPES keys.
        address: Optional address for future zoning-based items.
        constraints: Optional list of zone constraints (e.g. coastal_zone).
    """
    base_items = _BASE_CHECKLISTS.get(
        project_type, _BASE_CHECKLISTS["residential_construction"]
    )

    items = [
        ChecklistItem(name=item["name"], required=item["required"])
        for item in base_items
    ]

    for constraint in constraints or []:
        extra = _ZONE_EXTRA_ITEMS.get(constraint, [])
        for item in extra:
            items.append(ChecklistItem(name=item["name"], required=item["required"]))

    return DocumentChecklist(items=items)
