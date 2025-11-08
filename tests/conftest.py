"""Shared pytest fixtures for orchestrating the Docker-based test stack."""

from __future__ import annotations

import os
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import httpx
import pytest
from testcontainers.compose import DockerCompose

SERVICE_API = "fapi-db-tmpl"
SERVICE_DB = "db"
API_INTERNAL_PORT = 8000
DB_INTERNAL_PORT = 5432


def _wait_for_http(url: str, timeout: float = 120.0, interval: float = 2.0) -> None:
    """Poll an HTTP endpoint until it returns a successful response."""

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code < 500:
                return
        except httpx.RequestError:
            pass
        time.sleep(interval)
    raise TimeoutError(
        f"Service at {url} did not become ready within {timeout} seconds"
    )


@pytest.fixture(scope="session")
def docker_test_stack(
    pytestconfig: pytest.Config,
) -> Generator[dict[str, Any], None, None]:
    """Start the Docker Compose stack once for the entire pytest session."""

    project_dir = Path(pytestconfig.rootpath)
    compose_files = ["docker-compose.yml", "docker-compose.test.override.yml"]

    compose = DockerCompose(
        str(project_dir),
        compose_file_name=compose_files,
        pull=False,
    )

    with compose:
        compose.start()

        api_host = compose.get_service_host(SERVICE_API, API_INTERNAL_PORT)
        api_port = compose.get_service_port(SERVICE_API, API_INTERNAL_PORT)
        db_host = compose.get_service_host(SERVICE_DB, DB_INTERNAL_PORT)
        db_port = compose.get_service_port(SERVICE_DB, DB_INTERNAL_PORT)

        _wait_for_http(
            f"http://{api_host}:{api_port}/health", timeout=180.0, interval=3.0
        )

        os.environ.setdefault("USE_SQLITE", "false")

        yield {
            "api": {"host": api_host, "port": api_port},
            "db": {"host": db_host, "port": db_port},
        }
