"""Claim management service — lookup, timeline, pending issues."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from app.models.schemas import ClaimStatus

_MOCK_DATA_DIR = Path(__file__).resolve().parents[3] / "mock_data"

TIMELINES: dict[str, dict] = {
    "ui": {
        "claim_type": "UI",
        "estimated_days": 21,
        "steps": [
            {"step": 1, "name": "Claim Filed", "description": "Your claim has been received by EDD.", "estimated_days": 0},
            {"step": 2, "name": "Identity Verification", "description": "EDD verifies your identity via ID.me or documents.", "estimated_days": 3},
            {"step": 3, "name": "Employer Notification", "description": "Your former employer is notified and may respond.", "estimated_days": 10},
            {"step": 4, "name": "Eligibility Determination", "description": "EDD reviews your eligibility based on wages and separation reason.", "estimated_days": 5},
            {"step": 5, "name": "Benefit Calculation", "description": "Your weekly benefit amount is calculated.", "estimated_days": 2},
            {"step": 6, "name": "First Payment Issued", "description": "If approved, your first payment is issued after certification.", "estimated_days": 1},
        ],
    },
    "di": {
        "claim_type": "DI",
        "estimated_days": 14,
        "steps": [
            {"step": 1, "name": "Claim Filed", "description": "Your DI claim has been received.", "estimated_days": 0},
            {"step": 2, "name": "Physician Certification", "description": "EDD reviews your physician's medical certification.", "estimated_days": 5},
            {"step": 3, "name": "Eligibility Review", "description": "EDD verifies your SDI coverage and base period earnings.", "estimated_days": 5},
            {"step": 4, "name": "Benefit Determination", "description": "Your benefit amount is calculated and a notice is sent.", "estimated_days": 3},
            {"step": 5, "name": "First Payment Issued", "description": "Payment issued after the 7-day unpaid waiting period.", "estimated_days": 1},
        ],
    },
    "pfl": {
        "claim_type": "PFL",
        "estimated_days": 14,
        "steps": [
            {"step": 1, "name": "Claim Filed", "description": "Your PFL claim has been received.", "estimated_days": 0},
            {"step": 2, "name": "Documentation Review", "description": "EDD reviews your supporting documentation (birth certificate, medical cert, etc.).", "estimated_days": 5},
            {"step": 3, "name": "Eligibility Review", "description": "EDD verifies your SDI contributions and qualifying reason.", "estimated_days": 5},
            {"step": 4, "name": "Benefit Determination", "description": "Your benefit amount is calculated.", "estimated_days": 3},
            {"step": 5, "name": "First Payment Issued", "description": "Payment issued once claim is approved.", "estimated_days": 1},
        ],
    },
}

# Mock pending-issue database keyed by claim_id
PENDING_ISSUES_DB: dict[str, list[dict]] = {
    "UI-2025-2345678": [
        {"issue": "Identity verification required", "severity": "high", "since_date": "2025-03-01"},
        {"issue": "Employer response pending", "severity": "medium", "since_date": "2025-03-05"},
    ],
    "DI-2025-7654321": [
        {"issue": "Awaiting physician certification form DE 2525", "severity": "high", "since_date": "2025-03-06"},
    ],
    "PFL-2025-9876543": [
        {"issue": "Bonding claim — awaiting birth certificate", "severity": "medium", "since_date": "2025-03-11"},
    ],
}


def _load_sample_claims() -> list[dict]:
    path = _MOCK_DATA_DIR / "sample_claims.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def lookup_claim(claim_type: str, last_four_ssn: str, date_of_birth: str) -> ClaimStatus | None:
    """Look up a claim by type and last-four SSN (mock implementation).

    In mock mode we match by program field in sample_claims.json and return
    the first matching record.
    """
    claims = _load_sample_claims()
    ct = claim_type.lower()
    for claim in claims:
        if claim.get("program", "").lower() == ct:
            return ClaimStatus(
                claim_id=claim["claim_id"],
                claim_type=claim["program"].upper(),
                status=claim["status"],
                filed_date=datetime.fromisoformat(claim["filed_date"]),
                last_certified=None,
                weekly_benefit_amount=claim.get("weekly_benefit_amount") or 0.0,
                remaining_balance=(claim.get("max_benefit_amount") or 0.0) - (claim.get("benefits_paid_to_date") or 0.0),
                pending_issues=claim.get("notes", []),
                next_payment_date=None,
            )
    return None


def get_claim_timeline(claim_type: str) -> dict | None:
    """Return expected processing timeline for a claim type."""
    return TIMELINES.get(claim_type.lower())


def get_pending_issues(claim_id: str) -> list[dict]:
    """Return pending issues that may delay a claim."""
    return PENDING_ISSUES_DB.get(claim_id, [])
