from dev.mocks.services.mock_greeting_service import MockGreetingService
from src.fapi_db_tmpl.api.services.greeting_service import GreetingService


def test_greeting_service_returns_expected_message():
    service = GreetingService()

    assert service.generate_greeting("Tester") == "Hello, Tester"


def test_mock_greeting_service_returns_mock_message():
    service = MockGreetingService()

    assert service.generate_greeting("Tester") == "[mock] Hello, Tester"
