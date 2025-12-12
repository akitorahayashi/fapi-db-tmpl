"""API tests executed against the dockerized development stack."""

import pytest


@pytest.mark.asyncio
class TestDockerizedAPI:
    async def test_health_endpoint_returns_ok(self, async_client):
        response = await async_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_greeting_uses_mock_service_when_enabled(self, async_client):
        response = await async_client.get("/greetings/API")

        assert response.status_code == 200
        assert response.json() == {"message": "[mock] Hello, API"}

