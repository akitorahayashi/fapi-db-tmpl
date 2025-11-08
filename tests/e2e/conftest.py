from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def api_base_url(docker_test_stack: dict[str, dict[str, str | int]]) -> str:
    """Expose the base URL for the API service started by testcontainers."""

    api_info = docker_test_stack["api"]
    return f"http://{api_info['host']}:{api_info['port']}"
