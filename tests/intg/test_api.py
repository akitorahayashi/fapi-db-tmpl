"""Integration tests for the FastAPI application."""

import pytest


@pytest.mark.asyncio
async def test_intg_hello_world(async_client):
    """Integration smoke test for hello world endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World"}


@pytest.mark.asyncio
async def test_intg_health_check(async_client):
    """Integration smoke test for health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_intg_versioned_greeting(async_client):
    """Versioned greeting endpoint should return personalised responses."""
    response = await async_client.get("/v1/greetings/Integration")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Integration"}
