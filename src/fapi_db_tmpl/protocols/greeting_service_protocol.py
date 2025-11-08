"""Protocol for greeting service implementations."""

from typing import Protocol


class GreetingServiceProtocol(Protocol):
    """Contract for services capable of generating greetings."""

    def generate_greeting(self, name: str) -> str: ...
