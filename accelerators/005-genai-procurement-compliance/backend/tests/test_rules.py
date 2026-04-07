"""Tests for the rule engine."""

from app.services.rule_engine import get_rules, match_rules


class TestGetRules:
    """Tests for get_rules function."""

    def test_returns_all_rules(self):
        """Should return at least 18 rules covering all categories."""
        rules = get_rules()
        assert len(rules) >= 18

    def test_rule_structure(self):
        """Each rule should have the required fields."""
        rules = get_rules()
        for rule in rules:
            assert rule.id
            assert rule.category
            assert rule.requirement
            assert rule.source in ("EO N-5-26", "SB 53", "NIST")
            assert rule.severity in ("critical", "high", "medium", "low")
            assert isinstance(rule.keywords, list)
            assert len(rule.keywords) > 0

    def test_filter_by_eo(self):
        """Should return only EO N-5-26 rules when filtered."""
        rules = get_rules(source="eo-n-5-26")
        assert len(rules) > 0
        for rule in rules:
            assert rule.source == "EO N-5-26"

    def test_filter_by_sb53(self):
        """Should return only SB 53 rules when filtered."""
        rules = get_rules(source="sb-53")
        assert len(rules) > 0
        for rule in rules:
            assert rule.source == "SB 53"

    def test_filter_by_nist(self):
        """Should return only NIST rules when filtered."""
        rules = get_rules(source="nist")
        assert len(rules) > 0
        for rule in rules:
            assert rule.source == "NIST"

    def test_filter_by_unknown_returns_empty(self):
        """Unknown source filter should return empty list."""
        rules = get_rules(source="unknown-source")
        assert len(rules) == 0


class TestMatchRules:
    """Tests for match_rules function."""

    def test_match_with_attestation_text(self):
        """Sample attestation text should match multiple rules."""
        text = (
            "Our vendor provides content safety filters, bias testing with "
            "demographic parity analysis, and full transparency disclosure. "
            "We comply with CCPA for data privacy and maintain human oversight "
            "with escalation procedures."
        )
        matches = match_rules(text)
        assert len(matches) > 0
        categories = {m.category for m in matches}
        assert "content_safety" in categories
        assert "bias_governance" in categories

    def test_match_returns_confidence(self):
        """Matches should have confidence between 0 and 1."""
        text = "bias testing with demographic parity and fairness evaluation"
        matches = match_rules(text)
        for m in matches:
            assert 0 < m.confidence <= 1.0

    def test_match_with_no_keywords(self):
        """Text with no compliance keywords should return no matches."""
        text = "The weather today is sunny and warm."
        matches = match_rules(text)
        assert len(matches) == 0

    def test_matches_sorted_by_confidence(self):
        """Matches should be sorted by confidence descending."""
        text = "content safety bias testing transparency monitoring audit trail"
        matches = match_rules(text)
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i].confidence >= matches[i + 1].confidence

    def test_matched_keywords_populated(self):
        """Matched keywords list should contain actual matched terms."""
        text = "We implement content safety and content moderation."
        matches = match_rules(text)
        safety_matches = [m for m in matches if m.category == "content_safety"]
        assert len(safety_matches) > 0
        assert len(safety_matches[0].matched_keywords) > 0
