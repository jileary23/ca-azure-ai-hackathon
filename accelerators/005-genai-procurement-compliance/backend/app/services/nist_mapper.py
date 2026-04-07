"""NIST AI RMF risk classification and control mapping."""

from __future__ import annotations

from app.models.schemas import NistClassification, NistControl

# NIST AI RMF core functions and their associated controls
_NIST_FUNCTIONS: dict[str, dict] = {
    "Govern": {
        "description": "Cultivate and implement a culture of risk management",
        "keywords": [
            "governance",
            "policy",
            "accountability",
            "oversight",
            "leadership",
            "organization",
            "risk culture",
            "compliance",
        ],
        "controls": [
            NistControl(
                control_id="GV-1",
                function="Govern",
                title="Governance Policies",
                description="Establish and maintain AI governance policies and procedures",
            ),
            NistControl(
                control_id="GV-2",
                function="Govern",
                title="Accountability Structures",
                description="Define roles, responsibilities, and accountability for AI risk management",
            ),
            NistControl(
                control_id="GV-3",
                function="Govern",
                title="Risk Management Integration",
                description="Integrate AI risk management into enterprise risk management framework",
            ),
        ],
    },
    "Map": {
        "description": "Identify and understand AI risks in context",
        "keywords": [
            "context",
            "stakeholder",
            "impact",
            "use case",
            "deployment",
            "user",
            "environment",
            "scope",
            "requirements",
        ],
        "controls": [
            NistControl(
                control_id="MP-1",
                function="Map",
                title="Context Establishment",
                description="Establish the context for AI system deployment and intended use",
            ),
            NistControl(
                control_id="MP-2",
                function="Map",
                title="Stakeholder Engagement",
                description="Identify and engage relevant stakeholders in AI risk assessment",
            ),
            NistControl(
                control_id="MP-3",
                function="Map",
                title="Impact Assessment",
                description="Assess potential impacts of AI system on individuals and communities",
            ),
        ],
    },
    "Measure": {
        "description": "Analyze and assess AI risks and impacts",
        "keywords": [
            "measure",
            "metrics",
            "testing",
            "evaluation",
            "benchmark",
            "performance",
            "bias",
            "fairness",
            "accuracy",
            "validation",
        ],
        "controls": [
            NistControl(
                control_id="MS-1",
                function="Measure",
                title="Risk Metrics",
                description="Define and track metrics for AI system performance and risk",
            ),
            NistControl(
                control_id="MS-2",
                function="Measure",
                title="Bias Assessment",
                description="Conduct systematic bias and fairness assessments",
            ),
            NistControl(
                control_id="MS-3",
                function="Measure",
                title="Testing Protocols",
                description="Implement comprehensive testing and validation protocols",
            ),
        ],
    },
    "Manage": {
        "description": "Prioritize and act on AI risks",
        "keywords": [
            "manage",
            "mitigate",
            "monitor",
            "respond",
            "incident",
            "remediation",
            "continuous",
            "lifecycle",
            "decommission",
        ],
        "controls": [
            NistControl(
                control_id="MG-1",
                function="Manage",
                title="Risk Treatment",
                description="Develop and implement risk treatment plans for identified AI risks",
            ),
            NistControl(
                control_id="MG-2",
                function="Manage",
                title="Incident Response",
                description="Establish and maintain AI incident response capabilities",
            ),
            NistControl(
                control_id="MG-3",
                function="Manage",
                title="Continuous Monitoring",
                description="Implement continuous monitoring of AI systems in production",
            ),
        ],
    },
}


def classify_system(description: str) -> NistClassification:
    """Classify an AI system against NIST AI RMF categories.

    Maps keywords in the description to NIST AI RMF functions (Govern, Map,
    Measure, Manage) and determines applicable controls.
    """
    text_lower = description.lower()

    applicable_functions: list[str] = []
    all_controls: list[NistControl] = []

    for func_name, func_info in _NIST_FUNCTIONS.items():
        matched = any(kw in text_lower for kw in func_info["keywords"])
        if matched:
            applicable_functions.append(func_name)
            all_controls.extend(func_info["controls"])

    # If nothing matches, default to all functions (conservative approach)
    if not applicable_functions:
        applicable_functions = list(_NIST_FUNCTIONS.keys())
        for func_info in _NIST_FUNCTIONS.values():
            all_controls.extend(func_info["controls"])

    # Determine risk tier based on how many functions are implicated
    func_count = len(applicable_functions)
    if func_count >= 4:
        risk_tier = "high"
    elif func_count >= 2:
        risk_tier = "medium"
    else:
        risk_tier = "low"

    return NistClassification(
        risk_tier=risk_tier,
        applicable_functions=applicable_functions,
        controls=all_controls,
    )


def get_applicable_controls(classification: NistClassification) -> list[NistControl]:
    """Return the controls from a NIST classification."""
    return classification.controls
