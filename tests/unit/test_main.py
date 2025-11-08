from fastapi.testclient import TestClient

from src.fapi_db_tmpl.api.dependencies import get_app_settings, get_greeting_service
from src.fapi_db_tmpl.main import create_app


def _refresh_client() -> TestClient:
    get_greeting_service.cache_clear()
    get_app_settings.cache_clear()
    return TestClient(create_app())


def test_hello_world_default_service():
    """Default configuration should use the production greeting service."""

    client = _refresh_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World"}


def test_greeting_endpoint_personalised_response():
    """The versioned greeting endpoint should personalise the message."""

    client = _refresh_client()
    response = client.get("/v1/greetings/Alice")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice"}


def test_greeting_endpoint_uses_mock_when_enabled(monkeypatch):
    """Setting the mock toggle should switch the dependency to the mock service."""

    monkeypatch.setenv("FAPI_DB_TMPL_USE_MOCK_GREETING", "true")
    client = _refresh_client()

    response = client.get("/v1/greetings/Alice")

    assert response.status_code == 200
    assert response.json() == {"message": "[mock] Hello, Alice"}

    monkeypatch.delenv("FAPI_DB_TMPL_USE_MOCK_GREETING", raising=False)


def test_health_check():
    """Smoke test for health check endpoint."""

    client = _refresh_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
