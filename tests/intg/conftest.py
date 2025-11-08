"""Shared pytest fixtures for the fapi-db-tmpl project."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="session")
def app() -> FastAPI:
    import os

    os.environ["USE_MOCK_GREETING"] = "true"
    from src.fapi_db_tmpl.api.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    """Provide an async HTTP client for exercising the API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
