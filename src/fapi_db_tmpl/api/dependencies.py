"""Dependency providers shared across the application."""

from functools import lru_cache
from typing import TYPE_CHECKING

from .protocols import GreetingServiceProtocol
from .services.greeting_service import GreetingService
from ..config.app_settings import AppSettings

if TYPE_CHECKING:  # pragma: no cover - import only for typing
    pass


@lru_cache()
def get_app_settings() -> AppSettings:
    """Load and cache strongly-typed application settings."""

    return AppSettings()


@lru_cache()
def get_greeting_service() -> GreetingServiceProtocol:
    """Resolve the greeting service, optionally swapping in the mock implementation."""

    settings = get_app_settings()

    if settings.use_mock_greeting:
        try:
            from dev.mocks.services.mock_greeting_service import MockGreetingService

            return MockGreetingService()
        except ImportError as e:
            raise RuntimeError(
                "Mock greeting service is enabled but not found. "
                "Ensure 'dev' package is in PYTHONPATH for development."
            ) from e

    return GreetingService()
