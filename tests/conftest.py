"""Shared pytest fixtures and configuration for all tests."""

import os
from collections.abc import Generator
from typing import Any

import pytest
from dotenv import load_dotenv

# Constants
SQLITE_TEST_DB_PATH = "./test_db.sqlite3"


# Lazy imports to avoid DBSettings validation issues
def _get_db_imports():
    """Lazy import of database-related modules to avoid validation issues."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    from src.fapi_db_tmpl.api.main import app
    from src.fapi_db_tmpl.db.database import Base, create_db_session

    return (
        create_engine,
        Session,
        sessionmaker,
        Base,
        create_db_session,
        app,
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with dotenv loading."""
    load_dotenv()


@pytest.fixture(scope="session")
def db_engine(request: pytest.FixtureRequest) -> Generator[Any, None, None]:
    """
    Fixture that provides DB engine for the entire test session.

    USE_SQLITE=true: Uses SQLite for fast, isolated testing
    USE_SQLITE=false: Uses PostgreSQL container for realistic testing
    """
    (
        create_engine,
        Session,
        sessionmaker,
        Base,
        create_db_session,
        app,
    ) = _get_db_imports()

    if os.environ.get("USE_SQLITE", "true").lower() == "true":
        # SQLite case - fast, file-based database
        engine = create_engine(
            f"sqlite:///{SQLITE_TEST_DB_PATH}",
            connect_args={"check_same_thread": False},
        )

        # Create all tables from models
        Base.metadata.create_all(bind=engine)

        yield engine

        # Clean up: drop tables and remove file
        Base.metadata.drop_all(bind=engine)
        if os.path.exists(SQLITE_TEST_DB_PATH):
            os.remove(SQLITE_TEST_DB_PATH)

        engine.dispose()
        return

    # PostgreSQL case - this should be handled by db-specific conftest.py
    pytest.skip("PostgreSQL testing should be done in db/ or e2e/ directories")


@pytest.fixture
def db_session(db_engine: Any) -> Generator[Any, None, None]:
    """
    Provides a transaction-scoped database session for each test function.

    Each test gets a clean database state through transaction rollback,
    ensuring test isolation without database recreation.
    """
    (
        create_engine,
        Session,
        sessionmaker,
        Base,
        create_db_session,
        app,
    ) = _get_db_imports()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()

    # Override FastAPI's dependency injection for testing
    app.dependency_overrides[create_db_session] = lambda: db

    try:
        yield db
    finally:
        db.rollback()  # Ensure clean state for next test
        db.close()
        app.dependency_overrides.pop(create_db_session, None)
