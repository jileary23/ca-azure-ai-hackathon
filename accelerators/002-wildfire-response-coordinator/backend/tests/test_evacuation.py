"""Tests for evacuation service."""

import pytest
from app.services import evacuation_service


class TestEvacuationRoutes:
    def test_known_zone(self):
        route = evacuation_service.get_evacuation_routes("zone-b")
        assert route is not None
        assert route["zone_id"] == "zone-b"
        assert route["zone_name"] == "Zone B - Canyon"
        assert route["population"] == 8000
        assert route["primary_route"] == "Topanga Canyon Blvd South"
        assert route["alternate_route"] == "PCH East"

    def test_unknown_zone(self):
        route = evacuation_service.get_evacuation_routes("zone-z")
        assert route is None

    def test_route_has_estimated_time(self):
        route = evacuation_service.get_evacuation_routes("zone-a")
        assert route is not None
        assert route["estimated_time_minutes"] > 0

    def test_all_zones_have_routes(self):
        for zid in evacuation_service.EVACUATION_ZONES:
            route = evacuation_service.get_evacuation_routes(zid)
            assert route is not None
            assert route["primary_route"] != ""
            assert route["alternate_route"] != ""


class TestZoneStatus:
    def test_all_zones(self):
        zones = evacuation_service.get_zone_status()
        assert len(zones) == 5

    def test_single_zone(self):
        zones = evacuation_service.get_zone_status("zone-b")
        assert len(zones) == 1
        assert zones[0]["status"] == "order"

    def test_nonexistent_zone(self):
        zones = evacuation_service.get_zone_status("zone-zzz")
        assert zones == []

    def test_zone_status_values(self):
        zones = evacuation_service.get_zone_status()
        statuses = {z["status"] for z in zones}
        assert "order" in statuses
        assert "warning" in statuses
        assert "none" in statuses

    def test_zone_has_population(self):
        zones = evacuation_service.get_zone_status()
        for z in zones:
            assert z["population"] > 0


class TestEvacuationTime:
    def test_larger_population_takes_longer(self):
        time_a = evacuation_service.estimate_evacuation_time("zone-a")  # 15k
        time_e = evacuation_service.estimate_evacuation_time("zone-e")  # 40k
        assert time_e > time_a

    def test_minimum_30_minutes(self):
        for zid in evacuation_service.EVACUATION_ZONES:
            t = evacuation_service.estimate_evacuation_time(zid)
            assert t >= 30

    def test_unknown_zone_returns_zero(self):
        t = evacuation_service.estimate_evacuation_time("zone-zz")
        assert t == 0

    def test_reasonable_range(self):
        for zid in evacuation_service.EVACUATION_ZONES:
            t = evacuation_service.estimate_evacuation_time(zid)
            assert 30 <= t <= 600  # 30 min to 10 hours


class TestEvacuationZones:
    def test_five_zones(self):
        assert len(evacuation_service.EVACUATION_ZONES) == 5

    def test_zone_structure(self):
        z = evacuation_service.EVACUATION_ZONES["zone-a"]
        assert "name" in z
        assert "population" in z
        assert "primary_route" in z
        assert "alternate_route" in z
        assert "status" in z
