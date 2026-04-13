"""Shared fixtures for the red team adversarial testing framework.

Targets any accelerator via --accel flag and --base-url for custom endpoints.
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--accel",
        action="store",
        default="001",
        help="Accelerator ID to target (e.g., 001, 004). Determines the default port.",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Override base URL (e.g., https://accel-001.example.azurecontainerapps.io). "
             "If not set, defaults to http://localhost:800{accel}.",
    )


@pytest.fixture(scope="session")
def accel_id(request):
    return request.config.getoption("--accel")


@pytest.fixture(scope="session")
def base_url(request, accel_id):
    url = request.config.getoption("--base-url")
    if url:
        return url.rstrip("/")
    return f"http://localhost:800{accel_id}"


@pytest.fixture(scope="session")
def chat_url(base_url):
    return f"{base_url}/api/chat"


@pytest.fixture(scope="session")
def health_url(base_url):
    return f"{base_url}/health"
