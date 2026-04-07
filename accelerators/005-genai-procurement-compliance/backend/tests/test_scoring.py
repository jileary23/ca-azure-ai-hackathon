"""Tests for the scoring engine."""

import pytest

from app.services.scoring_engine import (
    COMPLIANCE_CATEGORIES,
    TOTAL_WEIGHT,
    classify_risk_tier,
    score_attestation,
)


class TestScoreAttestation:
    """Tests for score_attestation function."""

    def test_known_keywords_produce_score(self):
        """Text with known compliance keywords should produce a meaningful score."""
        text = (
            "Our system implements content safety filters and bias governance. "
            "We ensure civil rights protection and provide transparency disclosure. "
            "Data privacy is maintained with CCPA compliance. Human oversight with "
            "escalation procedures is in place. We conduct thorough risk assessment "
            "and testing validation including red team exercises."
        )
        result = score_attestation(text)
        assert result.overall_score > 0
        assert result.risk_tier in ("low", "medium", "high", "critical")
        assert isinstance(result.category_scores, dict)
        assert len(result.category_scores) == 18

    def test_empty_text_returns_zero_score(self):
        """Empty text should produce a score of zero with all categories as gaps."""
        result = score_attestation("")
        assert result.overall_score == 0.0
        assert result.risk_tier == "critical"
        assert len(result.gaps) == 18
        assert len(result.recommendations) == 18
        for cat in COMPLIANCE_CATEGORIES:
            assert result.category_scores[cat] == 0.0

    def test_partial_coverage(self):
        """Text covering only some categories should produce a partial score."""
        text = "We implement content safety and bias testing with fairness evaluation."
        result = score_attestation(text)
        assert 0 < result.overall_score < 100
        assert result.category_scores["content_safety"] > 0
        assert result.category_scores["bias_governance"] > 0
        # Categories not mentioned should be zero
        assert result.category_scores["environmental_impact"] == 0.0

    def test_full_coverage_high_score(self):
        """Text covering all categories should produce a high score."""
        parts = []
        for cat_info in COMPLIANCE_CATEGORIES.values():
            parts.extend(cat_info["keywords"][:2])
        text = " ".join(parts)
        result = score_attestation(text)
        assert result.overall_score >= 80
        assert result.risk_tier == "low"

    def test_gaps_sorted_by_severity(self):
        """Gaps should be sorted by severity (critical first)."""
        result = score_attestation("")
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        severities = [g["severity"] for g in result.gaps]
        for i in range(len(severities) - 1):
            assert severity_order[severities[i]] <= severity_order[severities[i + 1]]

    def test_score_between_0_and_100(self):
        """Score should always be between 0 and 100."""
        for text in ["", "random text", "content safety bias transparency privacy"]:
            result = score_attestation(text)
            assert 0 <= result.overall_score <= 100

    def test_total_weight_is_positive(self):
        """TOTAL_WEIGHT should be positive and match the sum of all category weights."""
        assert TOTAL_WEIGHT > 0
        assert TOTAL_WEIGHT == sum(c["weight"] for c in COMPLIANCE_CATEGORIES.values())


class TestClassifyRiskTier:
    """Tests for classify_risk_tier function."""

    @pytest.mark.parametrize(
        "score,expected",
        [
            (100.0, "low"),
            (85.0, "low"),
            (80.0, "low"),
            (79.9, "medium"),
            (60.0, "medium"),
            (59.9, "high"),
            (40.0, "high"),
            (39.9, "critical"),
            (0.0, "critical"),
        ],
    )
    def test_risk_tier_boundaries(self, score: float, expected: str):
        assert classify_risk_tier(score) == expected
