"""Tests for FPL service — guidelines and income limits."""

import pytest
from app.services.fpl_service import get_fpl_guidelines, get_income_limit
from app.services.magi_engine import BASE_FPL, MEDI_CAL_THRESHOLDS, calculate_fpl


class TestGetFPLGuidelines:
    def test_returns_year(self):
        result = get_fpl_guidelines()
        assert result["year"] == 2024

    def test_contains_all_categories(self):
        result = get_fpl_guidelines()
        returned_cats = {c["category"] for c in result["categories"]}
        assert returned_cats == set(MEDI_CAL_THRESHOLDS.keys())

    def test_household_sizes_1_to_8(self):
        result = get_fpl_guidelines()
        for cat in result["categories"]:
            limits = cat["income_limits_by_household_size"]
            assert set(limits.keys()) == set(range(1, 9))

    def test_limits_increase_with_household_size(self):
        result = get_fpl_guidelines()
        for cat in result["categories"]:
            limits = cat["income_limits_by_household_size"]
            for size in range(2, 9):
                assert limits[size] > limits[size - 1]

    def test_base_fpl_included(self):
        result = get_fpl_guidelines()
        assert result["base_fpl"] == BASE_FPL


class TestGetIncomeLimit:
    def test_adults_individual(self):
        limit = get_income_limit("adults_19_64", 1)
        expected = round(calculate_fpl(1) * 138 / 100, 2)
        assert limit == expected

    def test_children_family_of_4(self):
        limit = get_income_limit("children_6_18", 4)
        expected = round(calculate_fpl(4) * 266 / 100, 2)
        assert limit == expected

    def test_pregnant_household_of_2(self):
        limit = get_income_limit("pregnant", 2)
        expected = round(calculate_fpl(2) * 213 / 100, 2)
        assert limit == expected

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError, match="Unknown category"):
            get_income_limit("invalid_category", 1)
