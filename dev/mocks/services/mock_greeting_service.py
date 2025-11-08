"""Mock greeting service for local development and tests."""

from src.fapi_db_tmpl.protocols import GreetingServiceProtocol


class MockGreetingService(GreetingServiceProtocol):
    """Return a deterministic mock greeting useful for validation."""

    def generate_greeting(self, name: str) -> str:
        return f"[mock] Hello, {name}"


_: GreetingServiceProtocol = MockGreetingService()
