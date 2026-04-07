"""Tests for weather service."""

import pytest
from app.services import weather_service


class TestWeatherAlerts:
    def test_all_alerts(self):
        alerts = weather_service.get_weather_alerts()
        assert len(alerts) >= 5

    def test_filter_by_region(self):
        alerts = weather_service.get_weather_alerts(region="Butte County")
        assert len(alerts) >= 1
        for a in alerts:
            assert any("Butte" in r for r in a["regions"])

    def test_filter_nonexistent_region(self):
        alerts = weather_service.get_weather_alerts(region="Mars Colony")
        assert alerts == []

    def test_alert_structure(self):
        alerts = weather_service.get_weather_alerts()
        a = alerts[0]
        assert "alert_id" in a
        assert "type" in a
        assert "severity" in a
        assert "regions" in a
        assert "headline" in a
        assert "description" in a
        assert "issued" in a
        assert "expires" in a

    def test_red_flag_warning_exists(self):
        alerts = weather_service.get_weather_alerts()
        rfw = [a for a in alerts if a["type"] == "Red Flag Warning"]
        assert len(rfw) >= 1

    def test_case_insensitive_region(self):
        alerts = weather_service.get_weather_alerts(region="butte county")
        assert len(alerts) >= 1

    def test_partial_region_match(self):
        alerts = weather_service.get_weather_alerts(region="Ventura")
        assert len(alerts) >= 1


class TestFireWeather:
    def test_known_location(self):
        fw = weather_service.get_fire_weather("Butte County")
        assert fw["temperature_f"] == 102
        assert fw["humidity_pct"] == 10
        assert fw["fire_danger_level"] == "extreme"

    def test_unknown_location_defaults(self):
        fw = weather_service.get_fire_weather("Some Random Place")
        assert fw["location"] == "Some Random Place"
        assert fw["fire_danger_level"] == "moderate"

    def test_all_fire_danger_levels_valid(self):
        valid = {"low", "moderate", "high", "very_high", "extreme"}
        for loc in ["Butte County", "Los Angeles County", "Sacramento County", "San Diego County", "Fresno County"]:
            fw = weather_service.get_fire_weather(loc)
            assert fw["fire_danger_level"] in valid

    def test_case_insensitive(self):
        fw = weather_service.get_fire_weather("BUTTE COUNTY")
        assert fw["fire_danger_level"] == "extreme"

    def test_la_county(self):
        fw = weather_service.get_fire_weather("Los Angeles County")
        assert fw["fire_danger_level"] == "very_high"
        assert fw["wind_direction"] == "NE"


class TestRedFlagWarning:
    def test_active_for_butte(self):
        assert weather_service.is_red_flag_warning("Butte County") is True

    def test_not_active_for_sacramento(self):
        assert weather_service.is_red_flag_warning("Sacramento County") is False

    def test_active_for_santa_barbara(self):
        assert weather_service.is_red_flag_warning("Santa Barbara County") is True

    def test_not_active_for_unknown(self):
        assert weather_service.is_red_flag_warning("Unknown County") is False
