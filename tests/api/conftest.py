"""API-level tests against dockerized development stack."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import httpx
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def api_network() -> Network:
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def postgres_container(api_network: Network) -> PostgresContainer:
    pg_user = os.environ.get("POSTGRES_USER", "test")
    pg_password = os.environ.get("POSTGRES_PASSWORD", "test")
    pg_db = os.environ.get("POSTGRES_DB", "test")
    with (
        PostgresContainer(
            "postgres:16-alpine",
            username=pg_user,
            password=pg_password,
            dbname=pg_db,
        )
        .with_network(api_network)
        .with_network_aliases("db")
        .with_kwargs(log_config={"type": "json-file"}) as pg
    ):
        yield pg


@pytest.fixture(scope="session")
def api_image() -> str:
    # Use the temporary image built for dockerized API tests
    return os.environ.get("FAPI_DB_TMPL_E2E_IMAGE", "fapi-db-tmpl-e2e:latest")


@pytest.fixture(scope="session")
def api_base_url(
    api_image: str,
    postgres_container: PostgresContainer,
    api_network: Network,
) -> str:
    env = {
        "POSTGRES_HOST": "db",
        "POSTGRES_USER": postgres_container.username,
        "POSTGRES_PASSWORD": postgres_container.password,
        "POSTGRES_DB": postgres_container.dbname,
        # Development-target API tests use the mock greeting service
        "FAPI_DB_TMPL_USE_MOCK_GREETING": "true",
    }
    api_wait_strategy = HttpWaitStrategy(8000, "/health").for_status_code(200)
    with (
        DockerContainer(image=api_image)
        .with_network(api_network)
        .with_envs(**env)
        .with_exposed_ports(8000)
        .waiting_for(api_wait_strategy)
        .with_kwargs(log_config={"type": "json-file"}) as api
    ):
        host = api.get_container_host_ip()
        port = api.get_exposed_port(8000)
        base_url = f"http://{host}:{port}"
        print(f"\n🚀 API tests running against: {base_url}")
        yield base_url


@pytest.fixture
async def async_client(api_base_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=api_base_url) as client:
        yield client
