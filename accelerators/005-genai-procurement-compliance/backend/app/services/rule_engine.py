"""Rule matching service for compliance requirements."""

from __future__ import annotations

from app.models.schemas import ComplianceRuleDetail, RuleMatch

# Pre-populated rules covering the 18 EO N-5-26 compliance categories
_RULES: list[dict] = [
    {
        "id": "EON526-01",
        "category": "content_safety",
        "requirement": "AI systems must implement content safety filters to prevent generation of harmful outputs",
        "source": "EO N-5-26",
        "severity": "critical",
        "keywords": ["content safety", "safety filter", "harmful content", "content moderation", "toxicity"],
    },
    {
        "id": "EON526-02",
        "category": "bias_governance",
        "requirement": "Vendors must conduct and document bias testing across protected demographic groups",
        "source": "EO N-5-26",
        "severity": "critical",
        "keywords": ["bias", "bias testing", "demographic parity", "fairness", "disparate impact"],
    },
    {
        "id": "EON526-03",
        "category": "civil_rights_protection",
        "requirement": "AI systems must not discriminate against individuals based on protected characteristics",
        "source": "EO N-5-26",
        "severity": "critical",
        "keywords": ["civil rights", "discrimination", "protected class", "equal protection"],
    },
    {
        "id": "SB53-01",
        "category": "transparency_disclosure",
        "requirement": "AI system capabilities, limitations, and intended use must be publicly disclosed",
        "source": "SB 53",
        "severity": "high",
        "keywords": ["transparency", "disclosure", "explainability", "model card", "interpretability"],
    },
    {
        "id": "EON526-04",
        "category": "data_privacy",
        "requirement": "AI systems handling personal data must comply with CCPA/CPRA requirements",
        "source": "EO N-5-26",
        "severity": "high",
        "keywords": ["data privacy", "CCPA", "CPRA", "PII", "personal information", "data protection"],
    },
    {
        "id": "SB53-02",
        "category": "human_oversight",
        "requirement": "Human-in-the-loop oversight required for high-risk AI decision-making",
        "source": "SB 53",
        "severity": "high",
        "keywords": ["human oversight", "human-in-the-loop", "human review", "override", "escalation"],
    },
    {
        "id": "NIST-01",
        "category": "risk_assessment",
        "requirement": "Comprehensive risk assessment must be conducted before AI system deployment",
        "source": "NIST",
        "severity": "high",
        "keywords": ["risk assessment", "risk analysis", "impact assessment", "risk mitigation"],
    },
    {
        "id": "NIST-02",
        "category": "testing_validation",
        "requirement": "AI systems must undergo rigorous testing and validation before deployment",
        "source": "NIST",
        "severity": "high",
        "keywords": ["testing", "validation", "evaluation", "benchmark", "quality assurance", "red team"],
    },
    {
        "id": "SB53-03",
        "category": "incident_reporting",
        "requirement": "AI safety incidents must be reported within 72 hours to designated authorities",
        "source": "SB 53",
        "severity": "medium",
        "keywords": ["incident report", "incident response", "72 hours", "breach notification"],
    },
    {
        "id": "EON526-05",
        "category": "documentation",
        "requirement": "Complete technical documentation must be maintained for all AI systems",
        "source": "EO N-5-26",
        "severity": "medium",
        "keywords": ["documentation", "technical documentation", "system documentation", "specification"],
    },
    {
        "id": "EON526-06",
        "category": "training_competency",
        "requirement": "Staff operating AI systems must receive adequate training and certification",
        "source": "EO N-5-26",
        "severity": "medium",
        "keywords": ["training", "competency", "staff training", "certification", "education"],
    },
    {
        "id": "EON526-07",
        "category": "vendor_accountability",
        "requirement": "Vendors must accept contractual accountability for AI system performance and compliance",
        "source": "EO N-5-26",
        "severity": "medium",
        "keywords": ["vendor accountability", "SLA", "service level", "contractual obligation"],
    },
    {
        "id": "NIST-03",
        "category": "audit_trail",
        "requirement": "AI systems must maintain comprehensive audit logs for all decisions",
        "source": "NIST",
        "severity": "medium",
        "keywords": ["audit trail", "audit log", "logging", "traceability", "provenance"],
    },
    {
        "id": "NIST-04",
        "category": "model_governance",
        "requirement": "Model lifecycle governance including versioning, approval, and retirement processes",
        "source": "NIST",
        "severity": "medium",
        "keywords": ["model governance", "version control", "model lifecycle", "model registry"],
    },
    {
        "id": "EON526-08",
        "category": "deployment_monitoring",
        "requirement": "Continuous monitoring of AI systems in production for performance and drift",
        "source": "EO N-5-26",
        "severity": "medium",
        "keywords": ["monitoring", "deployment monitoring", "drift detection", "observability", "alerting"],
    },
    {
        "id": "SB53-04",
        "category": "feedback_mechanisms",
        "requirement": "Users must have accessible mechanisms to provide feedback and report issues",
        "source": "SB 53",
        "severity": "low",
        "keywords": ["feedback", "user feedback", "complaint", "grievance", "user reporting"],
    },
    {
        "id": "EON526-09",
        "category": "environmental_impact",
        "requirement": "Environmental impact of AI training and inference must be assessed and documented",
        "source": "EO N-5-26",
        "severity": "low",
        "keywords": ["environmental impact", "carbon footprint", "energy consumption", "sustainability"],
    },
    {
        "id": "SB53-05",
        "category": "accessibility",
        "requirement": "AI systems must meet accessibility standards including ADA and Section 508",
        "source": "SB 53",
        "severity": "low",
        "keywords": ["accessibility", "ADA", "WCAG", "section 508", "assistive technology"],
    },
    {
        "id": "NIST-05",
        "category": "risk_assessment",
        "requirement": "AI risk assessments must be updated periodically and after significant changes",
        "source": "NIST",
        "severity": "high",
        "keywords": ["risk assessment", "periodic review", "risk management", "risk evaluation"],
    },
    {
        "id": "EON526-10",
        "category": "data_privacy",
        "requirement": "Data minimization and purpose limitation must be enforced for AI training data",
        "source": "EO N-5-26",
        "severity": "high",
        "keywords": ["data minimization", "purpose limitation", "data retention", "data governance"],
    },
]

# Source filter mapping
_SOURCE_MAP = {
    "eo-n-5-26": "EO N-5-26",
    "sb-53": "SB 53",
    "nist": "NIST",
}


def _to_rule(raw: dict) -> ComplianceRuleDetail:
    return ComplianceRuleDetail(
        id=raw["id"],
        category=raw["category"],
        requirement=raw["requirement"],
        source=raw["source"],
        severity=raw["severity"],
        keywords=raw["keywords"],
    )


def get_rules(source: str | None = None) -> list[ComplianceRuleDetail]:
    """Return all compliance rules, optionally filtered by source."""
    rules = [_to_rule(r) for r in _RULES]
    if source:
        mapped = _SOURCE_MAP.get(source.lower(), source)
        rules = [r for r in rules if r.source == mapped]
    return rules


def match_rules(text: str) -> list[RuleMatch]:
    """Match text against compliance rules using keyword matching."""
    text_lower = text.lower()
    matches: list[RuleMatch] = []

    for raw in _RULES:
        matched_keywords = [kw for kw in raw["keywords"] if kw.lower() in text_lower]
        if matched_keywords:
            confidence = min(1.0, len(matched_keywords) / max(len(raw["keywords"]) / 2, 1))
            matches.append(
                RuleMatch(
                    rule_id=raw["id"],
                    category=raw["category"],
                    matched_keywords=matched_keywords,
                    confidence=round(confidence, 2),
                )
            )

    # Sort by confidence descending
    matches.sort(key=lambda m: m.confidence, reverse=True)
    return matches
