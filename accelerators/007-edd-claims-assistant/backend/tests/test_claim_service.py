"""Tests for claim_service."""

from app.services.claim_service import (
    lookup_claim,
    get_claim_timeline,
    get_pending_issues,
)


class TestLookupClaim:
    def test_lookup_ui(self):
        claim = lookup_claim("ui", "1234", "1990-01-15")
        assert claim is not None
        assert claim.claim_type == "UI"
        assert claim.claim_id == "UI-2025-1234567"

    def test_lookup_di(self):
        claim = lookup_claim("di", "5678", "1985-06-20")
        assert claim is not None
        assert claim.claim_type == "DI"

    def test_lookup_pfl(self):
        claim = lookup_claim("pfl", "9999", "1992-03-01")
        assert claim is not None
        assert claim.claim_type == "PFL"

    def test_lookup_unknown_type(self):
        claim = lookup_claim("xyz", "0000", "2000-01-01")
        assert claim is None


class TestGetClaimTimeline:
    def test_ui_timeline(self):
        tl = get_claim_timeline("ui")
        assert tl is not None
        assert tl["claim_type"] == "UI"
        assert tl["estimated_days"] == 21
        assert len(tl["steps"]) > 0

    def test_di_timeline(self):
        tl = get_claim_timeline("di")
        assert tl is not None
        assert tl["estimated_days"] == 14

    def test_pfl_timeline(self):
        tl = get_claim_timeline("pfl")
        assert tl is not None
        assert tl["estimated_days"] == 14

    def test_unknown_claim_type(self):
        tl = get_claim_timeline("xyz")
        assert tl is None


class TestGetPendingIssues:
    def test_known_claim(self):
        issues = get_pending_issues("UI-2025-2345678")
        assert len(issues) == 2
        assert issues[0]["issue"] == "Identity verification required"

    def test_unknown_claim(self):
        issues = get_pending_issues("NONEXISTENT")
        assert issues == []
