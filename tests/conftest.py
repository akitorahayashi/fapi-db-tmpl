"""Shared pytest fixtures and configuration for all tests."""

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with dotenv loading."""
    load_dotenv()
