"""Expert directory service."""

from app.models.schemas import ExpertInfo
from app.services.mock_service import EXPERTS_DB

# Extended expert directory covering all accelerator agencies
EXTENDED_EXPERTS: list[dict] = [
    {
        "expert_id": "EXP-007",
        "name": "Angela Martinez",
        "agency": "CDT",
        "department": "AI and Innovation Office",
        "expertise_areas": [
            "AI governance", "GenAI policy", "data privacy",
            "EO N-12-23", "technology strategy",
        ],
        "email": "angela.martinez@cdt.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-008",
        "name": "Kevin Nguyen",
        "agency": "CDT",
        "department": "Information Security Office",
        "expertise_areas": [
            "cybersecurity", "data governance", "cloud security",
            "FedRAMP", "StateRAMP",
        ],
        "email": "kevin.nguyen@cdt.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-009",
        "name": "Patricia Williams",
        "agency": "GovOps",
        "department": "Office of Digital Innovation",
        "expertise_areas": [
            "cross-agency collaboration", "digital services",
            "process improvement", "Envision 2026",
        ],
        "email": "patricia.williams@govops.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-010",
        "name": "Thomas Jackson",
        "agency": "OPR",
        "department": "CEQA Division",
        "expertise_areas": [
            "CEQA", "environmental review", "climate policy",
            "land use planning", "housing policy",
        ],
        "email": "thomas.jackson@opr.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-011",
        "name": "Deepa Rao",
        "agency": "DHCS",
        "department": "Eligibility Division",
        "expertise_areas": [
            "Medi-Cal eligibility", "healthcare policy",
            "managed care", "telehealth",
        ],
        "email": "deepa.rao@dhcs.ca.gov",
        "available": False,
    },
    {
        "expert_id": "EXP-012",
        "name": "Carlos Mendoza",
        "agency": "CDSS",
        "department": "Privacy Office",
        "expertise_areas": [
            "data sharing", "CCPA", "CPRA", "privacy compliance",
            "benefits data",
        ],
        "email": "carlos.mendoza@cdss.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-013",
        "name": "Jennifer Lee",
        "agency": "EDD",
        "department": "UI Division",
        "expertise_areas": [
            "unemployment insurance", "workforce development",
            "disability insurance", "claims adjudication",
        ],
        "email": "jennifer.lee@edd.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-014",
        "name": "Michael Brown",
        "agency": "DGS",
        "department": "Procurement Division",
        "expertise_areas": [
            "procurement", "vendor management", "IT acquisition",
            "state contracting", "SB 53 compliance",
        ],
        "email": "michael.brown@dgs.ca.gov",
        "available": True,
    },
    {
        "expert_id": "EXP-015",
        "name": "Samantha Park",
        "agency": "HCD",
        "department": "Housing Policy Division",
        "expertise_areas": [
            "housing policy", "permitting", "RHNA",
            "building standards", "affordable housing",
        ],
        "email": "samantha.park@hcd.ca.gov",
        "available": True,
    },
]


def _all_experts() -> list[dict]:
    return EXPERTS_DB + EXTENDED_EXPERTS


def find_experts(topic: str, agency: str | None = None) -> list[ExpertInfo]:
    """Find subject matter experts by topic."""
    tokens = [t.lower() for t in topic.split() if len(t) >= 2]
    results: list[ExpertInfo] = []

    for exp in _all_experts():
        if agency and exp["agency"] != agency:
            continue
        exp_text = (
            " ".join(exp["expertise_areas"]).lower()
            + " "
            + exp["department"].lower()
            + " "
            + exp["name"].lower()
        )
        if tokens and not any(t in exp_text for t in tokens):
            continue
        results.append(
            ExpertInfo(
                expert_id=exp["expert_id"],
                name=exp["name"],
                agency=exp["agency"],
                department=exp["department"],
                expertise_areas=exp["expertise_areas"],
                email=exp["email"],
                available=exp["available"],
            )
        )
    return results


def get_expert(expert_id: str) -> ExpertInfo | None:
    """Get expert details by ID."""
    for exp in _all_experts():
        if exp["expert_id"] == expert_id:
            return ExpertInfo(
                expert_id=exp["expert_id"],
                name=exp["name"],
                agency=exp["agency"],
                department=exp["department"],
                expertise_areas=exp["expertise_areas"],
                email=exp["email"],
                available=exp["available"],
            )
    return None
