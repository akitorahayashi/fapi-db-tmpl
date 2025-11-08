"""End-to-end tests for the FastAPI application."""

import pytest


class TestE2EAPI:
    """
    Class-based end-to-end tests for API endpoints.
    Tests run against the application with real database.
    """

    @pytest.mark.asyncio
    async def test_e2e_health_check(self, async_client):
        """End-to-end smoke test for health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_e2e_versioned_greeting(self, async_client):
        """End-to-end validation of the greeting endpoint."""
        response = await async_client.get("/greetings/E2E")
        assert response.status_code == 200
        assert response.json() == {"message": "[mock] Hello, E2E"}
