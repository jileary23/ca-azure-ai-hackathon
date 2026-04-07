"""Tests for PSPS (Public Safety Power Shutoff) service."""

import pytest
from app.services import psps_service


class TestPSPSStatus:
    def test_all_utilities(self):
        results = psps_service.get_psps_status()
        assert len(results) == 3

    def test_pge_active(self):
        results = psps_service.get_psps_status(utility="pge")
        assert len(results) == 1
        assert results[0]["utility_code"] == "pge"
        assert results[0]["status"] == "active"

    def test_sce_planned(self):
        results = psps_service.get_psps_status(utility="sce")
        assert len(results) == 1
        assert results[0]["status"] == "planned"

    def test_sdge_none(self):
        results = psps_service.get_psps_status(utility="sdge")
        assert len(results) == 1
        assert results[0]["status"] == "none"
        assert results[0]["affected_areas"] == []

    def test_unknown_utility(self):
        results = psps_service.get_psps_status(utility="unknown")
        assert results == []

    def test_status_has_utility_name(self):
        results = psps_service.get_psps_status()
        for r in results:
            assert "utility_name" in r
            assert r["utility_name"] != ""

    def test_active_has_restoration(self):
        results = psps_service.get_psps_status(utility="pge")
        assert results[0]["estimated_restoration"] is not None

    def test_none_no_restoration(self):
        results = psps_service.get_psps_status(utility="sdge")
        assert results[0]["estimated_restoration"] is None

    def test_case_insensitive(self):
        results = psps_service.get_psps_status(utility="PGE")
        # Our implementation lowercases the input
        assert len(results) == 1


class TestAffectedAreas:
    def test_pge_areas(self):
        areas = psps_service.get_affected_areas("pge")
        assert "Butte County" in areas
        assert len(areas) >= 3

    def test_sdge_no_areas(self):
        areas = psps_service.get_affected_areas("sdge")
        assert areas == []

    def test_unknown_utility(self):
        areas = psps_service.get_affected_areas("unknown")
        assert areas == []


class TestUtilities:
    def test_all_utilities_defined(self):
        assert "pge" in psps_service.UTILITIES
        assert "sce" in psps_service.UTILITIES
        assert "sdge" in psps_service.UTILITIES

    def test_utility_structure(self):
        for code, info in psps_service.UTILITIES.items():
            assert "name" in info
            assert "service_area" in info
