"""End-to-end test fixtures."""

import os

import httpx
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def e2e_network():
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def postgres_container(e2e_network):
    pg_user = os.environ.get("POSTGRES_USER", "test")
    pg_password = os.environ.get("POSTGRES_PASSWORD", "test")
    pg_db = os.environ.get("POSTGRES_DB", "test")
    with (
        PostgresContainer(
            "postgres:16-alpine", username=pg_user, password=pg_password, dbname=pg_db
        )
        .with_network(e2e_network)
        .with_network_aliases("db")
        .with_kwargs(log_config={"type": "json-file"}) as pg
    ):
        yield pg


@pytest.fixture(scope="session")
def api_image():
    # Use the temporary image built for e2e tests
    return "fapi-db-tmpl-e2e:latest"


@pytest.fixture(scope="session")
def api_base_url(api_image, postgres_container, e2e_network):
    env = {
        "USE_SQLITE": "false",
        "POSTGRES_HOST": "db",
        "POSTGRES_USER": postgres_container.username,
        "POSTGRES_PASSWORD": postgres_container.password,
        "POSTGRES_DB": postgres_container.dbname,
        "USE_MOCK_GREETING": "true",
    }
    api_wait_strategy = HttpWaitStrategy(8000, "/health").for_status_code(200)
    with (
        DockerContainer(image=api_image)
        .with_network(e2e_network)
        .with_envs(**env)
        .with_exposed_ports(8000)
        .waiting_for(api_wait_strategy)
        .with_kwargs(log_config={"type": "json-file"}) as api
    ):
        host = api.get_container_host_ip()
        port = api.get_exposed_port(8000)
        base_url = f"http://{host}:{port}"
        print(f"\n🚀 E2E API running at: {base_url}")
        yield base_url


@pytest.fixture
async def async_client(api_base_url):
    async with httpx.AsyncClient(base_url=api_base_url) as client:
        yield client
