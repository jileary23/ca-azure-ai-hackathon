"""ActionAgent — Generates eligibility determinations and responses with DHCS citations."""

import os
from app.models.schemas import (
    MediCalQuery,
    RoutingDecision,
    AgentResponse,
    Citation,
    EligibilityScreening,
    ApplicationStatus,
)
from app.services.mock_service import MockMediCalService


class ActionAgent:
    """Generates responses using DHCS policy knowledge and mock/live services."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockMediCalService()

    async def execute(self, query: MediCalQuery, routing: RoutingDecision) -> AgentResponse:
        """Execute action based on routing decision. Falls back to mock when live not ready."""
        if self.mock_mode:
            return self._handle_mock(query, routing)
        try:
            return self._handle_live(query, routing)
        except NotImplementedError:
            return self._handle_mock(query, routing)

    def _handle_live(self, query: MediCalQuery, routing: RoutingDecision) -> AgentResponse:
        """Live service integration — not yet implemented."""
        raise NotImplementedError("Live Azure services not yet configured")

    def _handle_mock(self, query: MediCalQuery, routing: RoutingDecision) -> AgentResponse:
        destination = routing.destination

        if destination == "eligibility_screening":
            return self._screen_eligibility(query)
        elif destination == "application_processing":
            return self._check_application(query)
        elif destination == "income_review":
            return self._review_income(query)
        elif destination == "document_verification":
            return self._document_help(query)
        elif destination == "county_services":
            return self._county_info(query)
        else:
            return self._general_response(query)

    def _screen_eligibility(self, query: MediCalQuery) -> AgentResponse:
        income = None
        household_size = query.entities.get("household_size", 1)
        if "income_amounts" in query.entities:
            income = query.entities["income_amounts"][0]

        if income is not None:
            screening = self.mock_service.screen_eligibility(
                monthly_income=income,
                household_size=household_size,
                program_type=query.program_type,
            )
            eligible_text = "likely eligible" if screening.likely_eligible else "may not qualify"
            response = (
                f"Based on a monthly income of ${income:,.2f} and household size of "
                f"{household_size}, you are {eligible_text} for {screening.program_type}. "
                f"Your income is at {screening.fpl_percentage:.0f}% of the Federal Poverty Level. "
                f"The income limit for your household is ${screening.income_limit:,.2f}/year."
            )
            return AgentResponse(
                response=response,
                confidence=screening.confidence,
                citations=[
                    Citation(source="DHCS MAGI Manual", text="Income eligibility thresholds per 42 CFR 435.603", regulation_ref="42 CFR 435.603"),
                    Citation(source="2024 FPL Guidelines", text="Federal Poverty Level guidelines published by HHS", regulation_ref="ASPE 2024 FPL"),
                ],
                eligibility=screening,
            )

        program_info = self.mock_service.get_program_info(query.program_type or "MAGI_Adult")
        return AgentResponse(
            response=program_info,
            confidence=0.85,
            citations=[
                Citation(source="DHCS Policy", text="Medi-Cal program overview and eligibility", regulation_ref="WIC §14005.7"),
            ],
        )

    def _check_application(self, query: MediCalQuery) -> AgentResponse:
        app_id = query.entities.get("application_id")
        app_status = self.mock_service.get_application_status(app_id)
        if app_status:
            return AgentResponse(
                response=f"Application {app_status.app_id} is currently '{app_status.status}'. {app_status.next_action or ''}",
                confidence=0.95,
                citations=[Citation(source="DHCS Application System", text="Application status lookup", regulation_ref=None)],
                application=app_status,
            )
        return AgentResponse(
            response="I can help you check your application status. Please provide your application ID (format: MC-YYYY-XXXXX).",
            confidence=0.7,
            citations=[],
        )

    def _review_income(self, query: MediCalQuery) -> AgentResponse:
        income = query.entities.get("income_amounts", [None])[0] if "income_amounts" in query.entities else None
        if income:
            household_size = query.entities.get("household_size", 1)
            screening = self.mock_service.screen_eligibility(monthly_income=income, household_size=household_size)
            return AgentResponse(
                response=f"Your reported income of ${income:,.2f}/month puts you at {screening.fpl_percentage:.0f}% FPL for a household of {household_size}. The MAGI income limit is ${screening.income_limit:,.2f}/year.",
                confidence=0.9,
                citations=[
                    Citation(source="DHCS Income Rules", text="MAGI methodology per ACA Section 1902(e)(14)", regulation_ref="ACA §1902(e)(14)"),
                ],
                eligibility=screening,
            )
        return AgentResponse(
            response="To verify your income for Medi-Cal, you'll need to provide documents such as pay stubs, W-2 forms, or tax returns. What type of income would you like to report?",
            confidence=0.8,
            citations=[
                Citation(source="DHCS Verification Guide", text="Acceptable income verification documents", regulation_ref="ACL 21-34"),
            ],
        )

    def _document_help(self, query: MediCalQuery) -> AgentResponse:
        docs = self.mock_service.get_required_documents()
        doc_list = "\n".join(f"- {d}" for d in docs)
        return AgentResponse(
            response=f"Common documents needed for Medi-Cal applications:\n{doc_list}\n\nYou can upload documents through the BenefitsCal portal or submit them to your county office.",
            confidence=0.88,
            citations=[
                Citation(source="DHCS Document Requirements", text="Verification document types", regulation_ref="ACL 21-34"),
            ],
        )

    def _county_info(self, query: MediCalQuery) -> AgentResponse:
        county = query.entities.get("county")
        office = self.mock_service.get_county_office(county)
        if office:
            return AgentResponse(
                response=f"The {office['name']} is located at {office['address']}. Phone: {office['phone']}. Hours: {office['hours']}.",
                confidence=0.92,
                citations=[Citation(source="DHCS County Directory", text="County social services office information", regulation_ref=None)],
            )
        return AgentResponse(
            response="Which county are you in? I can help you find your local Medi-Cal office. Major counties include Los Angeles, San Diego, San Francisco, Sacramento, and Fresno.",
            confidence=0.75,
            citations=[],
        )

    def _general_response(self, query: MediCalQuery) -> AgentResponse:
        return AgentResponse(
            response="I can help you with Medi-Cal eligibility screening, application status, income verification, document requirements, and county office information. What would you like to know?",
            confidence=0.7,
            citations=[
                Citation(source="DHCS", text="Medi-Cal program information", regulation_ref="WIC §14000"),
            ],
        )
