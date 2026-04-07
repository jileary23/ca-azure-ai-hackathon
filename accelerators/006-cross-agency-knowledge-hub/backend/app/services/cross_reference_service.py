"""Policy relationship detection service."""

from app.models.schemas import CrossReference
from app.services.mock_service import CROSS_REFERENCES_DB, DOCUMENTS_DB

RELATIONSHIP_TYPES = [
    "supersedes",
    "implements",
    "references",
    "contradicts",
    "supplements",
    "complements",
    "cites",
]

# Extended cross-references for expanded document set
EXTENDED_CROSS_REFS: list[dict] = [
    {
        "source_doc_id": "POL-CDT-2024-001",
        "target_doc_id": "POL-CDT-2024-002",
        "relationship": "implements",
        "description": "CDT AI Use Policy implements the data governance framework requirements.",
    },
    {
        "source_doc_id": "POL-CDT-2024-001",
        "target_doc_id": "POL-CDSS-2024-003",
        "relationship": "references",
        "description": "CDT AI Use Policy references CDSS Data Sharing and Privacy Policy for PII handling.",
    },
    {
        "source_doc_id": "GUID-OPR-2024-001",
        "target_doc_id": "GUID-OPR-2024-002",
        "relationship": "supplements",
        "description": "CEQA Guidelines supplement the Climate Action Plan for environmental review.",
    },
    {
        "source_doc_id": "PROC-GovOps-2024-001",
        "target_doc_id": "POL-CDT-2024-002",
        "relationship": "references",
        "description": "Cross-Agency Collaboration Procedures reference CDT Data Governance Framework.",
    },
    {
        "source_doc_id": "POL-DHCS-2024-002",
        "target_doc_id": "FAQ-DHCS-2024-002",
        "relationship": "supplements",
        "description": "Medi-Cal Provider Handbook supplements the Eligibility FAQ with provider-side details.",
    },
    {
        "source_doc_id": "GUID-EDD-2024-001",
        "target_doc_id": "PROC-EDD-2024-001",
        "relationship": "implements",
        "description": "UI Program Guide implements claims processing procedures for field staff.",
    },
]


def _all_refs() -> list[dict]:
    return CROSS_REFERENCES_DB + EXTENDED_CROSS_REFS


def find_cross_references(doc_id: str) -> list[CrossReference]:
    """Find related policies/documents for a given document."""
    results = []
    for ref in _all_refs():
        if ref["source_doc_id"] == doc_id or ref["target_doc_id"] == doc_id:
            results.append(
                CrossReference(
                    source_doc_id=ref["source_doc_id"],
                    target_doc_id=ref["target_doc_id"],
                    relationship=ref["relationship"],
                    description=ref["description"],
                )
            )
    return results


def detect_relationship(doc_a_id: str, doc_b_id: str) -> str | None:
    """Detect relationship type between two documents."""
    for ref in _all_refs():
        if (
            (ref["source_doc_id"] == doc_a_id and ref["target_doc_id"] == doc_b_id)
            or (ref["source_doc_id"] == doc_b_id and ref["target_doc_id"] == doc_a_id)
        ):
            return ref["relationship"]
    return None
