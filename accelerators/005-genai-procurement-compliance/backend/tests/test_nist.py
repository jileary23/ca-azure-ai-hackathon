"""Tests for the NIST AI RMF mapper."""

from app.services.nist_mapper import classify_system, get_applicable_controls


class TestClassifySystem:
    """Tests for classify_system function."""

    def test_returns_valid_classification(self):
        """Should return a classification with valid risk tier and functions."""
        result = classify_system("AI system for governance and policy compliance monitoring")
        assert result.risk_tier in ("low", "medium", "high")
        assert len(result.applicable_functions) > 0
        assert all(f in ("Govern", "Map", "Measure", "Manage") for f in result.applicable_functions)

    def test_govern_keywords(self):
        """Description with governance keywords should include Govern function."""
        result = classify_system("governance and policy accountability oversight")
        assert "Govern" in result.applicable_functions

    def test_map_keywords(self):
        """Description with context/stakeholder keywords should include Map function."""
        result = classify_system("stakeholder impact assessment and deployment context")
        assert "Map" in result.applicable_functions

    def test_measure_keywords(self):
        """Description with testing/metrics keywords should include Measure function."""
        result = classify_system("metrics testing evaluation benchmark performance bias assessment")
        assert "Measure" in result.applicable_functions

    def test_manage_keywords(self):
        """Description with management keywords should include Manage function."""
        result = classify_system("mitigate monitor respond incident remediation lifecycle")
        assert "Manage" in result.applicable_functions

    def test_all_functions_high_risk(self):
        """Description matching all functions should be classified as high risk."""
        text = (
            "governance policy accountability stakeholder impact "
            "metrics testing evaluation monitor incident remediation"
        )
        result = classify_system(text)
        assert len(result.applicable_functions) == 4
        assert result.risk_tier == "high"

    def test_no_keywords_defaults_all(self):
        """Description with no matching keywords should default to all functions."""
        result = classify_system("simple calculator application")
        assert len(result.applicable_functions) == 4
        assert result.risk_tier == "high"
        assert len(result.controls) > 0

    def test_controls_populated(self):
        """Classification should include relevant controls."""
        result = classify_system("AI system with governance oversight")
        assert len(result.controls) > 0
        for ctrl in result.controls:
            assert ctrl.control_id
            assert ctrl.function
            assert ctrl.title
            assert ctrl.description


class TestGetApplicableControls:
    """Tests for get_applicable_controls function."""

    def test_returns_controls_from_classification(self):
        """Should return the controls from the given classification."""
        classification = classify_system("governance and testing system")
        controls = get_applicable_controls(classification)
        assert len(controls) > 0
        assert controls == classification.controls
