"""Permission service tests — public vs state_employee vs admin."""

from app.services import permission_service
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── Unit tests ─────────────────────────────────────────────────────────


def test_public_access():
    agencies = permission_service.get_accessible_agencies("public")
    assert "CDT" in agencies
    assert "GovOps" in agencies
    assert "OPR" in agencies
    # Public should NOT see restricted agencies
    assert "CDSS" not in agencies
    assert "DHCS" not in agencies


def test_state_employee_access():
    agencies = permission_service.get_accessible_agencies("state_employee")
    assert "CDT" in agencies
    assert "CDSS" in agencies
    assert "DHCS" in agencies
    assert "EDD" in agencies
    assert "CalHR" in agencies


def test_admin_access():
    agencies = permission_service.get_accessible_agencies("admin")
    # Admin sees all agencies
    assert len(agencies) == len(permission_service.AGENCY_DIRECTORY)
    assert "CDT" in agencies
    assert "CDSS" in agencies


def test_unknown_role():
    agencies = permission_service.get_accessible_agencies("unknown_role")
    assert agencies == []


def test_check_permission_public_allowed():
    assert permission_service.check_permission("public", "CDT") is True
    assert permission_service.check_permission("public", "GovOps") is True


def test_check_permission_public_denied():
    assert permission_service.check_permission("public", "CDSS") is False
    assert permission_service.check_permission("public", "EDD") is False


def test_check_permission_admin_all():
    assert permission_service.check_permission("admin", "CDT") is True
    assert permission_service.check_permission("admin", "CDSS") is True
    assert permission_service.check_permission("admin", "EDD") is True


def test_check_permission_unknown_role():
    assert permission_service.check_permission("visitor", "CDT") is False


def test_get_agency_info():
    info = permission_service.get_agency_info("public")
    codes = [a["agency_code"] for a in info]
    assert "CDT" in codes
    assert all("agency_name" in a for a in info)


# ── API endpoint tests ─────────────────────────────────────────────────


def test_api_agencies_public():
    response = client.get("/api/agencies?role=public")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["role"] == "public"


def test_api_agencies_state_employee():
    response = client.get("/api/agencies?role=state_employee")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 3


def test_api_agencies_admin():
    response = client.get("/api/agencies?role=admin")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(permission_service.AGENCY_DIRECTORY)
