"""ActionAgent — Generates compliance analysis responses."""

import os

from app.models.schemas import (
    AgentResponse,
    Citation,
    ComplianceQuery,
    RoutingDecision,
)
from app.services.mock_service import MockComplianceService


class ActionAgent:
    """Third stage: produces compliance scores, gap analyses, and risk tiers."""

    def __init__(self) -> None:
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockComplianceService()

    async def act(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        if not self.mock_mode:
            try:
                return self._handle_live(query, routing)
            except NotImplementedError:
                pass  # fall back to mock

        handler = self._HANDLERS.get(query.intent, self._handle_general)
        return handler(self, query, routing)

    def _handle_live(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        """Live service integration — not yet implemented."""
        raise NotImplementedError("Live Azure services not yet configured")

    def _handle_compliance_check(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        vendor = query.entities.get("vendor_name")
        score = self.mock_service.get_compliance_score(vendor)
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Compliance score: {score.overall_score}/100 "
                f"(Risk: {score.risk_classification}). "
                f"Compliant: {score.compliant_count}, "
                f"Non-compliant: {score.non_compliant_count}, "
                f"Partial: {score.partial_count}."
            ),
            confidence=0.92,
            citations=[
                Citation(source="EO N-5-26", text="Executive Order N-5-26 vendor attestation requirements", regulation="EO_N-5-26"),
                Citation(source="SB 53", text="SB 53 AI safety evaluation standards", regulation="SB_53"),
            ],
            data={"compliance_score": score.model_dump()},
        )

    def _handle_gap_analysis(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        vendor = query.entities.get("vendor_name")
        gaps = self.mock_service.get_gap_analysis(vendor)
        gap_texts = [f"• {g.category}: {g.requirement} (severity: {g.severity})" for g in gaps.gaps[:5]]
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Gap analysis identified {len(gaps.gaps)} issues:\n" + "\n".join(gap_texts)
            ),
            confidence=0.88,
            citations=[
                Citation(source="NIST AI RMF", text="NIST AI Risk Management Framework gap assessment", regulation="NIST_AI_RMF"),
                Citation(source="EO N-5-26", text="Executive Order N-5-26 requirements checklist", regulation="EO_N-5-26"),
            ],
            data={"gap_analysis": gaps.model_dump()},
        )

    def _handle_attestation_upload(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        doc = self.mock_service.create_attestation()
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Attestation document received (ID: {doc.doc_id}). "
                f"Status: {doc.status}. Analysis will begin shortly."
            ),
            confidence=0.95,
            citations=[
                Citation(source="CDT", text="California Department of Technology attestation process"),
            ],
            data={"attestation": doc.model_dump(mode="json")},
        )

    def _handle_risk_assessment(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        vendor = query.entities.get("vendor_name")
        risk = self.mock_service.get_risk_classification(vendor)
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Risk classification: Tier {risk.tier} ({risk.classification}). "
                f"Justification: {risk.justification}"
            ),
            confidence=0.90,
            citations=[
                Citation(source="EO N-5-26", text="Risk tiering framework per EO N-5-26", regulation="EO_N-5-26"),
                Citation(source="NIST AI RMF", text="NIST AI RMF risk categorization", regulation="NIST_AI_RMF"),
            ],
            data={"risk": risk.model_dump()},
        )

    def _handle_regulation_lookup(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        rules = self.mock_service.get_rules()
        rule_texts = [f"• [{r.rule_id}] {r.requirement} ({r.regulation_source}, {r.severity})" for r in rules[:5]]
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Found {len(rules)} compliance rules. Top entries:\n" + "\n".join(rule_texts)
            ),
            confidence=0.85,
            citations=[
                Citation(source="EO N-5-26", text="Executive Order N-5-26", regulation="EO_N-5-26"),
                Citation(source="SB 53", text="SB 53 — AI Safety", regulation="SB_53"),
                Citation(source="NIST AI RMF", text="NIST AI Risk Management Framework", regulation="NIST_AI_RMF"),
            ],
        )

    def _handle_vendor_comparison(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        vendors = self.mock_service.get_all_vendor_scores()
        lines = [f"• {name}: {score.overall_score}/100 ({score.risk_classification})" for name, score in vendors.items()]
        return AgentResponse(
            intent=query.intent,
            response_text="Vendor compliance comparison:\n" + "\n".join(lines),
            confidence=0.87,
            citations=[
                Citation(source="CDT", text="CDT vendor compliance benchmarking"),
            ],
            data={"vendor_scores": {k: v.model_dump() for k, v in vendors.items()}},
        )

    def _handle_general(
        self, query: ComplianceQuery, routing: RoutingDecision
    ) -> AgentResponse:
        return AgentResponse(
            intent=query.intent,
            response_text=(
                "I can help with GenAI procurement compliance. Ask about "
                "compliance checks, gap analysis, risk assessment, regulation "
                "lookup, vendor comparison, or attestation uploads."
            ),
            confidence=0.50,
            citations=[
                Citation(source="CDT", text="California Department of Technology GenAI procurement guidance"),
            ],
        )

    _HANDLERS: dict = {
        "compliance_check": _handle_compliance_check,
        "gap_analysis": _handle_gap_analysis,
        "attestation_upload": _handle_attestation_upload,
        "risk_assessment": _handle_risk_assessment,
        "regulation_lookup": _handle_regulation_lookup,
        "vendor_comparison": _handle_vendor_comparison,
        "general_info": _handle_general,
    }
