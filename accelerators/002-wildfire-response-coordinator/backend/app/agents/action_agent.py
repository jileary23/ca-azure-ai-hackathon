"""ActionAgent — Generates tactical response recommendations for wildfire incidents."""

import os
from app.models.schemas import (
    IncidentQuery, RoutingDecision, AgentResponse, Citation,
    IncidentSummary, ResourceAllocation, EvacuationInfo,
)
from app.services.mock_service import MockWildfireService


class ActionAgent:
    """Generates actionable intelligence for wildfire response operations."""

    def __init__(self):
        self.mock_mode = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
        self.mock_service = MockWildfireService()

    async def execute(self, query: IncidentQuery, routing: RoutingDecision) -> AgentResponse:
        """Execute action based on routing decision. Falls back to mock when live not ready."""
        if self.mock_mode:
            return self._handle_mock(query, routing)
        try:
            return self._handle_live(query, routing)
        except NotImplementedError:
            return self._handle_mock(query, routing)

    def _handle_live(self, query: IncidentQuery, routing: RoutingDecision) -> AgentResponse:
        """Live service integration — not yet implemented."""
        raise NotImplementedError("Live services not yet configured")

    def _handle_mock(self, query: IncidentQuery, routing: RoutingDecision) -> AgentResponse:
        destination = routing.destination

        if destination == "incident_command":
            return self._incident_briefing(query)
        elif destination == "resource_management":
            return self._resource_allocation(query)
        elif destination == "evacuation_ops":
            return self._evacuation_info(query)
        elif destination == "weather_ops":
            return self._weather_briefing(query)
        elif destination == "utility_coordination":
            return self._psps_info(query)
        elif destination == "interagency":
            return self._agency_coordination(query)
        else:
            return self._general_response(query)

    def _incident_briefing(self, query: IncidentQuery) -> AgentResponse:
        incident_id = query.entities.get("incident_id")
        if incident_id:
            incident = self.mock_service.get_incident(incident_id)
            if incident:
                summary = IncidentSummary(
                    incident_id=incident.incident_id,
                    name=incident.name,
                    incident_type=incident.incident_type,
                    severity=incident.severity,
                    location=incident.location,
                    containment_pct=incident.containment_pct,
                    status=incident.status,
                    lead_agency=incident.lead_agency,
                )
                response = (
                    f"**{incident.name}** ({incident.incident_id})\n"
                    f"Type: {incident.incident_type} | Severity: {incident.severity}\n"
                    f"Location: {incident.location}, {incident.county} County\n"
                    f"Acres: {incident.acres_burned:,.0f} | Containment: {incident.containment_pct}%\n"
                    f"Status: {incident.status} | Lead: {incident.lead_agency}"
                )
                return AgentResponse(
                    response=response, confidence=0.95,
                    citations=[Citation(source="ICS Protocols", text="Incident status report per ICS-209", agency="CAL FIRE")],
                    incident=summary,
                )

        # Return all active incidents
        incidents = self.mock_service.get_all_incidents()
        active = [i for i in incidents if i.status == "active"]
        lines = [f"**Active Incidents ({len(active)}):**"]
        for inc in active:
            lines.append(f"- {inc.name} ({inc.incident_id}): {inc.acres_burned:,.0f} acres, {inc.containment_pct}% contained — {inc.location}")

        first = active[0] if active else None
        summary = None
        if first:
            summary = IncidentSummary(
                incident_id=first.incident_id, name=first.name,
                incident_type=first.incident_type, severity=first.severity,
                location=first.location, containment_pct=first.containment_pct,
                status=first.status, lead_agency=first.lead_agency,
            )

        return AgentResponse(
            response="\n".join(lines), confidence=0.9,
            citations=[Citation(source="CAL FIRE Incident Feed", text="Active incident summary", agency="CAL FIRE")],
            incident=summary,
        )

    def _resource_allocation(self, query: IncidentQuery) -> AgentResponse:
        requested_types = query.entities.get("resource_types", [])
        resources = self.mock_service.get_available_resources(requested_types)

        if resources:
            lines = [f"**Available Resources ({len(resources)}):**"]
            for r in resources[:10]:
                eta = f", ETA: {r.eta_minutes} min" if r.eta_minutes else ""
                lines.append(f"- {r.resource_id}: {r.resource_type} x{r.quantity} ({r.agency}) — {r.status}{eta}")

            return AgentResponse(
                response="\n".join(lines), confidence=0.9,
                citations=[Citation(source="Cal OES Procedures", text="Resource allocation per mutual aid agreement", agency="Cal OES")],
                resources=resources[:10],
            )

        return AgentResponse(
            response="No matching resources currently available. Initiating mutual aid request to adjacent regions.",
            confidence=0.7,
            citations=[Citation(source="Cal OES Mutual Aid", text="Mutual aid resource request protocol", agency="Cal OES")],
        )

    def _evacuation_info(self, query: IncidentQuery) -> AgentResponse:
        evac_info = self.mock_service.get_evacuation_info()

        lines = [f"**Evacuation Status** — {evac_info.total_evacuated:,} evacuated, {evac_info.shelters_open} shelters open"]
        for zone in evac_info.zones:
            status_emoji = {"order": "🔴", "warning": "🟡", "shelter_in_place": "🟠", "lifted": "🟢"}.get(zone.status, "⚪")
            lines.append(f"{status_emoji} **{zone.zone_name}** ({zone.status}): {zone.population:,} residents")
            if zone.routes:
                lines.append(f"  Routes: {', '.join(zone.routes)}")
            if zone.shelters:
                lines.append(f"  Shelters: {', '.join(zone.shelters)}")

        return AgentResponse(
            response="\n".join(lines), confidence=0.92,
            citations=[
                Citation(source="Cal OES Procedures", text="Evacuation zone management protocol", agency="Cal OES"),
                Citation(source="CAL FIRE SOP", text="Evacuation notification procedures", agency="CAL FIRE"),
            ],
            evacuation=evac_info,
        )

    def _weather_briefing(self, query: IncidentQuery) -> AgentResponse:
        county = query.entities.get("county")
        weather_data = self.mock_service.get_weather(county)

        lines = ["**Fire Weather Briefing:**"]
        for w in weather_data:
            flag = " ⚠️ RED FLAG WARNING" if w.red_flag_warning else ""
            watch = " 🔶 Fire Weather Watch" if w.fire_weather_watch else ""
            lines.append(
                f"- **{w.location}**: {w.temperature_f}°F, {w.humidity_pct}% humidity, "
                f"wind {w.wind_speed_mph} mph {w.wind_direction}{flag}{watch}"
            )
            lines.append(f"  Forecast: {w.forecast_summary}")

        return AgentResponse(
            response="\n".join(lines), confidence=0.88,
            citations=[Citation(source="NWS Fire Weather", text="National Weather Service fire weather forecast", agency="NWS")],
        )

    def _psps_info(self, query: IncidentQuery) -> AgentResponse:
        events = self.mock_service.get_psps_events()
        if not events:
            return AgentResponse(
                response="No active or planned PSPS events at this time.",
                confidence=0.85,
                citations=[],
            )

        lines = [f"**Public Safety Power Shutoff Events ({len(events)}):**"]
        for e in events:
            lines.append(
                f"- {e.utility} ({e.status}): {e.affected_customers:,} customers affected"
            )
            lines.append(f"  Areas: {', '.join(e.affected_areas)}")
            if e.estimated_restoration:
                lines.append(f"  Est. restoration: {e.estimated_restoration.strftime('%Y-%m-%d %H:%M')}")

        return AgentResponse(
            response="\n".join(lines), confidence=0.85,
            citations=[Citation(source="CPUC PSPS Protocols", text="Public Safety Power Shutoff coordination", agency="CPUC")],
        )

    def _agency_coordination(self, query: IncidentQuery) -> AgentResponse:
        assignments = self.mock_service.get_agency_assignments()
        lines = ["**Inter-Agency Coordination:**"]
        for a in assignments:
            lines.append(f"- **{a.agency}**: {a.role} — {a.resources_committed} resources committed")
            lines.append(f"  Contact: {a.contact}")

        return AgentResponse(
            response="\n".join(lines), confidence=0.88,
            citations=[
                Citation(source="ICS Protocols", text="Unified command structure per NIMS", agency="Cal OES"),
                Citation(source="Cal OES Procedures", text="Mutual aid coordination", agency="Cal OES"),
            ],
        )

    def _general_response(self, query: IncidentQuery) -> AgentResponse:
        return AgentResponse(
            response=(
                "I can help with: incident status reports, resource allocation, "
                "evacuation zone information, weather briefings, PSPS events, and "
                "inter-agency coordination. What do you need?"
            ),
            confidence=0.7,
            citations=[Citation(source="CAL FIRE SOP", text="Emergency coordination system overview", agency="CAL FIRE")],
        )
