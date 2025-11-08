"""Shared pytest fixtures for the fapi-db-tmpl project."""

import pytest


@pytest.fixture(autouse=True)
def mock_env_for_integration_tests(monkeypatch):
    """Set up environment variables for all integration tests."""
    # Use mock implementations to avoid real network calls
    monkeypatch.setenv("USE_SQLITE", "true")
    monkeypatch.setenv("USE_MOCK_GREETING", "true")
