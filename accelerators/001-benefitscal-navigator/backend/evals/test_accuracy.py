"""Accuracy evaluation tests for BenefitsCal Navigator."""

import json
import os
import pytest
from pathlib import Path
from app.agents.query_agent import QueryAgent
from app.agents.action_agent import ActionAgent
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
def action_agent():
    os.environ["USE_MOCK_SERVICES"] = "true"
    return ActionAgent()


@pytest.fixture
def router_agent():
    return RouterAgent()


class TestIntentAccuracy:
    @pytest.mark.asyncio
    async def test_intent_detection_accuracy(self, eval_cases, query_agent):
        """Verify intent detection matches expected intents for benefits queries."""
        correct = 0
        total = len(eval_cases)
        for case in eval_cases:
            result = await query_agent.process(case["input"])
            if result.intent == case["expected_intent"]:
                correct += 1
        accuracy = correct / total
        assert accuracy >= 0.7, f"Intent accuracy {accuracy:.0%} below 70% threshold"


class TestResponseQuality:
    @pytest.mark.asyncio
    async def test_responses_are_nonempty(self, eval_cases, query_agent, router_agent, action_agent):
        """All benefits eval cases should produce non-empty responses."""
        for case in eval_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            assert result.response, f"Empty response for case {case['id']}"

    @pytest.mark.asyncio
    async def test_confidence_reasonable(self, eval_cases, query_agent, router_agent, action_agent):
        """All responses should have confidence > 0."""
        for case in eval_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            assert result.confidence > 0, f"Zero confidence for case {case['id']}"

    @pytest.mark.asyncio
    async def test_citations_present(self, eval_cases, query_agent, router_agent, action_agent):
        """Most benefits responses should include citations to policy sources."""
        cases_with_citations = 0
        for case in eval_cases:
            query = await query_agent.process(case["input"])
            routing = await router_agent.route(query)
            result = await action_agent.execute(query, routing)
            if result.citations:
                cases_with_citations += 1
        assert cases_with_citations / len(eval_cases) >= 0.5
