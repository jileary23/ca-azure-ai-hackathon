"""Routing evaluation tests for BenefitsCal Navigator."""

import json
import pytest
from pathlib import Path
from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent


EVAL_CONFIG = Path(__file__).parent / "eval_config.json"


@pytest.fixture
def eval_cases():
    with open(EVAL_CONFIG) as f:
        data = json.load(f)
    return data["test_cases"]


@pytest.fixture
def query_agent():
    return QueryAgent()


@pytest.fixture
def router_agent():
    return RouterAgent()


class TestRoutingAccuracy:
    @pytest.mark.asyncio
    async def test_routing_accuracy(self, eval_cases, query_agent, router_agent):
        """Verify routing matches expected program/service destinations."""
        route_cases = [c for c in eval_cases if "expected_route" in c]
        correct = 0
        for case in route_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            if routing.destination == case["expected_route"]:
                correct += 1
        accuracy = correct / len(route_cases) if route_cases else 0
        assert accuracy >= 0.7, f"Routing accuracy {accuracy:.0%} below 70% threshold"


class TestEscalationDetection:
    @pytest.mark.asyncio
    async def test_escalation_cases(self, eval_cases, query_agent, router_agent):
        """Verify escalation triggers for crisis/urgent benefit cases."""
        escalation_cases = [c for c in eval_cases if c.get("expected_escalation")]
        detected = 0
        for case in escalation_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            if routing.escalate:
                detected += 1
        if escalation_cases:
            accuracy = detected / len(escalation_cases)
            assert accuracy >= 0.5, f"Escalation detection {accuracy:.0%} below 50% threshold"


class TestPriorityAssignment:
    @pytest.mark.asyncio
    async def test_critical_priority_cases(self, query_agent, router_agent):
        """Emergency/homeless/food insecurity should be critical priority."""
        critical_cases = [
            ("I'm homeless and need food today", "critical"),
            ("Can I get emergency food assistance right now?", "critical"),
        ]
        for msg, expected in critical_cases:
            query = await query_agent.process(msg)
            routing = await router_agent.route(query)
            assert routing.priority == expected, (
                f"'{msg}' should be {expected}, got {routing.priority}"
            )

    @pytest.mark.asyncio
    async def test_low_priority_general_info(self, query_agent, router_agent):
        """General info requests should be low priority."""
        query = await query_agent.process("What is CalFresh?")
        routing = await router_agent.route(query)
        assert routing.priority == "low"
