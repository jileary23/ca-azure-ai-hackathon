"""Mock Document Intelligence OCR service for income verification documents."""

MOCK_EXTRACTIONS: dict[str, dict] = {
    "w2": {
        "employer": "State of California — Dept. of Technology",
        "wages": 52_000.00,
        "federal_tax": 7_800.00,
        "state_tax": 3_120.00,
        "social_security": 3_224.00,
        "medicare": 754.00,
        "tax_year": 2024,
    },
    "pay_stub": {
        "employer": "Kaiser Permanente",
        "gross_pay": 4_333.33,
        "net_pay": 3_250.00,
        "pay_period": "bi-weekly",
        "ytd_gross": 26_000.00,
        "deductions": {
            "federal_tax": 650.00,
            "state_tax": 260.00,
            "health_insurance": 173.33,
        },
    },
    "tax_return": {
        "filing_status": "single",
        "agi": 48_500.00,
        "total_income": 52_000.00,
        "taxable_income": 35_500.00,
        "tax_exempt_interest": 0.00,
        "social_security_benefits": 0.00,
        "tax_year": 2024,
    },
    "bank_statement": {
        "bank_name": "Wells Fargo",
        "account_type": "checking",
        "statement_period": "2024-03-01 to 2024-03-31",
        "beginning_balance": 3_200.00,
        "ending_balance": 2_850.00,
        "total_deposits": 4_333.33,
        "total_withdrawals": 4_683.33,
    },
}

SUPPORTED_DOCUMENT_TYPES = list(MOCK_EXTRACTIONS.keys())

# Required documents by application type
REQUIRED_DOCUMENTS: dict[str, list[str]] = {
    "standard": [
        "photo_id",
        "proof_of_income",
        "proof_of_residency",
        "social_security_card",
    ],
    "pregnancy": [
        "photo_id",
        "proof_of_income",
        "proof_of_residency",
        "social_security_card",
        "proof_of_pregnancy",
    ],
    "disability": [
        "photo_id",
        "proof_of_income",
        "proof_of_residency",
        "social_security_card",
        "disability_certification",
        "bank_statement",
    ],
    "aged": [
        "photo_id",
        "proof_of_income",
        "proof_of_residency",
        "social_security_card",
        "medicare_card",
        "bank_statement",
    ],
}


def analyze_document(document_type: str, content: str = "") -> dict:
    """Mock OCR extraction from income verification documents.

    Args:
        document_type: One of "w2", "pay_stub", "tax_return", "bank_statement".
        content: Optional raw content (ignored in mock mode).

    Returns:
        Dict with extracted_data, confidence, document_type, fields_found.
    """
    doc_type = document_type.lower().replace("-", "_").replace(" ", "_")
    extracted = MOCK_EXTRACTIONS.get(doc_type)

    if extracted is None:
        return {
            "document_type": document_type,
            "extracted_data": {},
            "confidence": 0.0,
            "fields_found": 0,
            "error": f"Unsupported document type: {document_type}",
        }

    return {
        "document_type": doc_type,
        "extracted_data": extracted,
        "confidence": 0.95,
        "fields_found": len(extracted),
    }


def check_document_completeness(
    submitted_docs: list[str],
    required_docs: list[str] | None = None,
    application_type: str = "standard",
) -> dict:
    """Check whether all required documents have been submitted.

    Returns:
        Dict with complete, missing, submitted, progress_pct.
    """
    if required_docs is None:
        required_docs = REQUIRED_DOCUMENTS.get(
            application_type, REQUIRED_DOCUMENTS["standard"]
        )

    submitted_set = {d.lower().replace("-", "_").replace(" ", "_") for d in submitted_docs}
    required_set = {d.lower().replace("-", "_").replace(" ", "_") for d in required_docs}

    missing = sorted(required_set - submitted_set)
    submitted_valid = sorted(required_set & submitted_set)
    progress = (len(submitted_valid) / len(required_set) * 100) if required_set else 100.0

    return {
        "complete": len(missing) == 0,
        "missing": missing,
        "submitted": sorted(submitted_set),
        "progress_pct": round(progress, 1),
    }
