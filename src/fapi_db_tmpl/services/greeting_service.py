"""Production greeting service implementation."""


class GreetingService:
    """Generate simple greeting messages."""

    def generate_greeting(self, name: str) -> str:
        return f"Hello, {name}"
