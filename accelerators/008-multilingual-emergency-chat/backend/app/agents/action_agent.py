"""ActionAgent — Generates responses using mock or live services."""

import os

from app.models.schemas import (
    AgentResponse,
    Citation,
    EmergencyQuery,
    RoutingDecision,
)
from app.services.mock_service import MockEmergencyService


class ActionAgent:
    """Third stage: retrieves data and builds the response."""

    def __init__(self) -> None:
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockEmergencyService()

    async def act(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        if not self.mock_mode:
            try:
                return self._handle_live(query, routing)
            except NotImplementedError:
                pass  # fall back to mock

        handler = self._HANDLERS.get(query.intent, self._handle_general)
        return handler(self, query, routing)

    def _handle_live(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        """Live service integration — not yet implemented."""
        raise NotImplementedError("Live services not yet configured")

    # ---- intent handlers ------------------------------------------------

    def _handle_alerts(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        alerts = self.mock_service.get_alerts(query.emergency_type)
        alert_dicts = [a.model_dump(mode="json") for a in alerts]
        titles = ", ".join(a.title for a in alerts) if alerts else "none"
        return AgentResponse(
            intent=query.intent,
            response_text=f"Current active alerts: {titles}. Stay tuned for updates from Cal OES.",
            confidence=0.92,
            citations=[
                Citation(source="Cal OES", text="California Office of Emergency Services alert feed"),
                Citation(source="NWS", text="National Weather Service California region"),
            ],
            data={"alerts": alert_dicts},
        )

    def _handle_evacuation(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        orders = self.mock_service.get_evacuation_orders(query.emergency_type)
        order_dicts = [o.model_dump(mode="json") for o in orders]
        if orders:
            text = "; ".join(
                f"{o.zone_name}: {o.status}" for o in orders
            )
            response_text = f"Evacuation status — {text}. Follow official instructions."
        else:
            response_text = "No active evacuation orders at this time. Monitor Cal OES for updates."
        return AgentResponse(
            intent=query.intent,
            response_text=response_text,
            confidence=0.90,
            citations=[
                Citation(source="Cal OES", text="Official evacuation orders"),
                Citation(source="CAL FIRE", text="CAL FIRE incident updates"),
            ],
            data={"evacuation_orders": order_dicts},
        )

    def _handle_shelters(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        shelters = self.mock_service.get_shelters(query.location)
        shelter_dicts = [s.model_dump(mode="json") for s in shelters]
        if shelters:
            names = ", ".join(s.name for s in shelters[:3])
            response_text = f"Nearby shelters: {names}. Contact local authorities for current availability."
        else:
            response_text = "No shelters found for your area. Call 211 for assistance."
        return AgentResponse(
            intent=query.intent,
            response_text=response_text,
            confidence=0.88,
            citations=[
                Citation(source="Cal OES", text="Emergency shelter registry"),
                Citation(source="Red Cross", text="American Red Cross shelter locator"),
            ],
            data={"shelters": shelter_dicts},
        )

    def _handle_air_quality(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        report = self.mock_service.get_air_quality(query.location)
        return AgentResponse(
            intent=query.intent,
            response_text=(
                f"Air quality in {report.location}: AQI {report.aqi} ({report.category}). "
                f"{report.health_guidance}"
            ),
            confidence=0.93,
            citations=[
                Citation(source="CARB", text="California Air Resources Board"),
                Citation(source="AirNow", text="EPA AirNow real-time AQI data"),
            ],
            data={"air_quality": report.model_dump(mode="json")},
        )

    def _handle_safety(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        return AgentResponse(
            intent=query.intent,
            response_text=(
                "Emergency preparedness tips: 1) Build an emergency kit with water, food, "
                "medications, and documents. 2) Create a family communication plan. "
                "3) Know your evacuation routes. 4) Sign up for local alerts at "
                "CalAlerts.org. 5) Keep your phone charged and have a battery backup."
            ),
            confidence=0.85,
            citations=[
                Citation(source="Cal OES", text="California emergency preparedness guide"),
                Citation(source="FEMA", text="Ready.gov emergency planning resources"),
            ],
        )

    def _handle_general(
        self, query: EmergencyQuery, routing: RoutingDecision
    ) -> AgentResponse:
        return AgentResponse(
            intent=query.intent,
            response_text=(
                "I can help with emergency information for California. "
                "Ask about active alerts, evacuation orders, nearby shelters, "
                "air quality, or safety tips. For life-threatening emergencies, call 911."
            ),
            confidence=0.50,
            citations=[
                Citation(source="Cal OES", text="California Office of Emergency Services"),
            ],
        )

    _HANDLERS: dict = {
        "active_alerts": _handle_alerts,
        "evacuation_status": _handle_evacuation,
        "shelter_search": _handle_shelters,
        "air_quality": _handle_air_quality,
        "safety_tips": _handle_safety,
        "general_info": _handle_general,
    }
