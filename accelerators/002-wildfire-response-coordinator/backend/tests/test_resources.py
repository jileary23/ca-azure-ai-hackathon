"""Tests for resource allocation service."""

import pytest
from app.services import resource_service


@pytest.fixture(autouse=True)
def reset_state():
    resource_service.reset()
    yield
    resource_service.reset()


class TestAvailableResources:
    def test_all_regions(self):
        results = resource_service.get_available_resources()
        assert len(results) > 0
        regions = {r["region"] for r in results}
        assert regions == {1, 2, 3, 4, 5, 6}

    def test_single_region(self):
        results = resource_service.get_available_resources(region=6)
        assert len(results) > 0
        assert all(r["region"] == 6 for r in results)

    def test_single_resource_type(self):
        results = resource_service.get_available_resources(resource_type="fire_engines")
        assert len(results) > 0
        assert all(r["resource_type"] == "fire_engines" for r in results)

    def test_region_and_type(self):
        results = resource_service.get_available_resources(region=6, resource_type="helicopters")
        assert len(results) == 1
        assert results[0]["available"] == 4

    def test_unknown_region(self):
        results = resource_service.get_available_resources(region=99)
        assert results == []

    def test_region_name_present(self):
        results = resource_service.get_available_resources(region=1)
        assert results[0]["region_name"] == "Region I"
        assert results[0]["coordinator"] == "Redding OES"

    def test_all_resource_types_present(self):
        results = resource_service.get_available_resources(region=2)
        types = {r["resource_type"] for r in results}
        assert types == set(resource_service.RESOURCE_TYPES)


class TestAllocateResources:
    def test_basic_allocation(self):
        alloc = resource_service.allocate_resources(
            incident_id="INC-2025-001",
            resource_type="fire_engines",
            quantity=3,
            from_region=2,
        )
        assert alloc["allocation_id"].startswith("ALLOC-")
        assert alloc["incident_id"] == "INC-2025-001"
        assert alloc["resource_type"] == "fire_engines"
        assert alloc["quantity"] == 3
        assert alloc["from_region"] == 2
        assert alloc["status"] == "dispatched"

    def test_default_region(self):
        alloc = resource_service.allocate_resources(
            incident_id="INC-2025-001",
            resource_type="helicopters",
            quantity=1,
        )
        assert alloc["from_region"] == 2

    def test_invalid_resource_type(self):
        with pytest.raises(ValueError, match="Unknown resource type"):
            resource_service.allocate_resources(
                incident_id="INC-1", resource_type="tanks", quantity=1,
            )

    def test_invalid_region(self):
        with pytest.raises(ValueError, match="Unknown region"):
            resource_service.allocate_resources(
                incident_id="INC-1", resource_type="fire_engines",
                quantity=1, from_region=99,
            )


class TestAllocationStatus:
    def test_empty(self):
        result = resource_service.get_allocation_status("INC-NONE")
        assert result == []

    def test_tracks_allocations(self):
        resource_service.allocate_resources("INC-1", "fire_engines", 2, 1)
        resource_service.allocate_resources("INC-1", "helicopters", 1, 1)
        resource_service.allocate_resources("INC-2", "dozers", 3, 2)

        inc1 = resource_service.get_allocation_status("INC-1")
        assert len(inc1) == 2
        inc2 = resource_service.get_allocation_status("INC-2")
        assert len(inc2) == 1


class TestMutualAidRegions:
    def test_all_six_regions(self):
        assert len(resource_service.MUTUAL_AID_REGIONS) == 6

    def test_region_counties(self):
        r6 = resource_service.MUTUAL_AID_REGIONS[6]
        assert "Los Angeles" in r6["counties"]
        assert "San Diego" in r6["counties"]

    def test_resource_types_list(self):
        assert "fire_engines" in resource_service.RESOURCE_TYPES
        assert "air_tankers" in resource_service.RESOURCE_TYPES
        assert "search_rescue" in resource_service.RESOURCE_TYPES
