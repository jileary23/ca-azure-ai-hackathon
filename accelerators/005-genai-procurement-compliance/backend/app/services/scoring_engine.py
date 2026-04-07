"""Severity-weighted compliance scoring engine for EO N-5-26 attestations."""

from __future__ import annotations

from app.models.schemas import ComplianceScoreDetail

# 18 EO N-5-26 compliance categories with severity weights
COMPLIANCE_CATEGORIES: dict[str, dict] = {
    "content_safety": {
        "weight": 10,
        "severity": "critical",
        "keywords": [
            "content safety",
            "content moderation",
            "harmful content",
            "safety filter",
            "toxicity",
            "content policy",
        ],
    },
    "bias_governance": {
        "weight": 10,
        "severity": "critical",
        "keywords": [
            "bias",
            "fairness",
            "demographic parity",
            "equalized odds",
            "disparate impact",
            "bias testing",
            "bias governance",
        ],
    },
    "civil_rights_protection": {
        "weight": 10,
        "severity": "critical",
        "keywords": [
            "civil rights",
            "discrimination",
            "protected class",
            "equal protection",
            "civil liberties",
            "non-discrimination",
        ],
    },
    "transparency_disclosure": {
        "weight": 8,
        "severity": "high",
        "keywords": [
            "transparency",
            "disclosure",
            "explainability",
            "interpretability",
            "model card",
            "documentation",
        ],
    },
    "data_privacy": {
        "weight": 8,
        "severity": "high",
        "keywords": [
            "data privacy",
            "privacy",
            "CCPA",
            "CPRA",
            "PII",
            "personal information",
            "data protection",
            "data minimization",
        ],
    },
    "human_oversight": {
        "weight": 8,
        "severity": "high",
        "keywords": [
            "human oversight",
            "human-in-the-loop",
            "human review",
            "override",
            "escalation",
            "manual review",
        ],
    },
    "risk_assessment": {
        "weight": 7,
        "severity": "high",
        "keywords": [
            "risk assessment",
            "risk analysis",
            "risk management",
            "risk mitigation",
            "impact assessment",
            "risk evaluation",
        ],
    },
    "testing_validation": {
        "weight": 7,
        "severity": "high",
        "keywords": [
            "testing",
            "validation",
            "evaluation",
            "benchmark",
            "test suite",
            "quality assurance",
            "red team",
        ],
    },
    "incident_reporting": {
        "weight": 6,
        "severity": "medium",
        "keywords": [
            "incident report",
            "incident response",
            "breach notification",
            "72 hours",
            "incident management",
            "post-incident",
        ],
    },
    "documentation": {
        "weight": 6,
        "severity": "medium",
        "keywords": [
            "documentation",
            "system documentation",
            "technical documentation",
            "user guide",
            "specification",
            "design document",
        ],
    },
    "training_competency": {
        "weight": 5,
        "severity": "medium",
        "keywords": [
            "training",
            "competency",
            "staff training",
            "education",
            "certification",
            "skill development",
        ],
    },
    "vendor_accountability": {
        "weight": 5,
        "severity": "medium",
        "keywords": [
            "vendor accountability",
            "vendor responsibility",
            "SLA",
            "service level",
            "contractual obligation",
            "vendor audit",
        ],
    },
    "audit_trail": {
        "weight": 5,
        "severity": "medium",
        "keywords": [
            "audit trail",
            "audit log",
            "logging",
            "traceability",
            "record keeping",
            "provenance",
        ],
    },
    "model_governance": {
        "weight": 4,
        "severity": "medium",
        "keywords": [
            "model governance",
            "model management",
            "version control",
            "model lifecycle",
            "model registry",
            "model approval",
        ],
    },
    "deployment_monitoring": {
        "weight": 4,
        "severity": "medium",
        "keywords": [
            "deployment monitoring",
            "monitoring",
            "observability",
            "performance monitoring",
            "drift detection",
            "alerting",
        ],
    },
    "feedback_mechanisms": {
        "weight": 3,
        "severity": "low",
        "keywords": [
            "feedback",
            "user feedback",
            "complaint",
            "grievance",
            "feedback mechanism",
            "user reporting",
        ],
    },
    "environmental_impact": {
        "weight": 2,
        "severity": "low",
        "keywords": [
            "environmental impact",
            "carbon footprint",
            "energy consumption",
            "sustainability",
            "green AI",
            "environmental",
        ],
    },
    "accessibility": {
        "weight": 2,
        "severity": "low",
        "keywords": [
            "accessibility",
            "ADA",
            "WCAG",
            "assistive technology",
            "inclusive design",
            "section 508",
        ],
    },
}

TOTAL_WEIGHT = sum(cat["weight"] for cat in COMPLIANCE_CATEGORIES.values())


def _match_category(text_lower: str, keywords: list[str]) -> list[str]:
    """Return which keywords from a category appear in the text."""
    return [kw for kw in keywords if kw.lower() in text_lower]


def score_attestation(attestation_text: str) -> ComplianceScoreDetail:
    """Score a vendor attestation against the 18 EO N-5-26 compliance categories.

    For mock mode: scans text for keywords matching each category.
    Score = (sum of matched category weights) / (sum of all weights) * 100.
    """
    text_lower = attestation_text.lower()

    category_scores: dict[str, float] = {}
    gaps: list[dict[str, str]] = []
    recommendations: list[str] = []
    matched_weight = 0.0

    for cat_name, cat_info in COMPLIANCE_CATEGORIES.items():
        matched_kws = _match_category(text_lower, cat_info["keywords"])
        if matched_kws:
            # Score proportional to how many keywords matched (max 100 per category)
            cat_score = min(100.0, (len(matched_kws) / max(len(cat_info["keywords"]) / 2, 1)) * 100)
            category_scores[cat_name] = round(cat_score, 1)
            matched_weight += cat_info["weight"]
        else:
            category_scores[cat_name] = 0.0
            gaps.append({
                "category": cat_name,
                "severity": cat_info["severity"],
                "description": f"No evidence found for {cat_name.replace('_', ' ')}",
            })
            recommendations.append(
                f"Address {cat_info['severity']}-severity gap: add {cat_name.replace('_', ' ')} documentation"
            )

    overall_score = round((matched_weight / TOTAL_WEIGHT) * 100, 1) if TOTAL_WEIGHT > 0 else 0.0
    risk_tier = classify_risk_tier(overall_score)

    # Sort recommendations by severity (critical first)
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda g: severity_order.get(g["severity"], 4))
    recommendations.sort(
        key=lambda r: next(
            (severity_order[s] for s in severity_order if s in r), 4
        )
    )

    return ComplianceScoreDetail(
        overall_score=overall_score,
        risk_tier=risk_tier,
        category_scores=category_scores,
        gaps=gaps,
        recommendations=recommendations,
    )


def classify_risk_tier(score: float) -> str:
    """Classify overall score into a risk tier."""
    if score >= 80:
        return "low"
    elif score >= 60:
        return "medium"
    elif score >= 40:
        return "high"
    else:
        return "critical"
