import os
from collections.abc import AsyncGenerator, Generator
from typing import Any

from dotenv import load_dotenv

load_dotenv()
if "POSTGRES_DB" not in os.environ and os.environ.get("POSTGRES_TEST_DB"):
    os.environ["POSTGRES_DB"] = os.environ["POSTGRES_TEST_DB"]

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session, sessionmaker

from src.fapi_db_tmpl import config as config_module
from src.fapi_db_tmpl.config import db_settings
from src.fapi_db_tmpl.config.db_settings import DBSettings
from src.fapi_db_tmpl.db import database as database_module
from src.fapi_db_tmpl.db.database import Base, create_db_session, get_engine
from src.fapi_db_tmpl.main import app

# Load .env and determine current DB settings
settings = db_settings


def _reset_engine() -> None:
    """Clear cached SQLAlchemy factory state so new settings take effect."""

    database_module._engine = None
    database_module._SessionLocal = None


def _configure_postgres(stack_db_info: dict[str, Any]) -> dict[str, Any]:
    """Override environment and settings based on dynamic Compose ports."""

    global settings

    original_env = {
        "USE_SQLITE": os.environ.get("USE_SQLITE"),
        "POSTGRES_HOST": os.environ.get("POSTGRES_HOST"),
        "POSTGRES_PORT": os.environ.get("POSTGRES_PORT"),
    }
    original_settings_obj = settings

    db_host = str(stack_db_info["host"])
    db_port = int(stack_db_info["port"])

    os.environ["USE_SQLITE"] = "false"
    os.environ["POSTGRES_HOST"] = db_host
    os.environ["POSTGRES_PORT"] = str(db_port)

    new_settings = DBSettings()

    settings = new_settings
    config_module.db_settings = new_settings
    database_module.db_settings = new_settings

    _reset_engine()

    return {"env": original_env, "settings_obj": original_settings_obj}


@pytest.fixture(scope="session")
def db_engine(request: pytest.FixtureRequest):
    """
    Fixture that provides DB engine for the entire test session.
    USE_SQLITE=true case (sqlt-test):
        - Creates all tables (create_all) for SQLite DB and returns engine.
        - Drops all tables (drop_all) at session end.
    USE_SQLITE=false case (pstg-test):
        - Returns engine for PostgreSQL migrated by entrypoint.sh.
        - (Does not create/drop tables)
    """
    global settings

    if settings.use_sqlite:
        engine = get_engine()

        # For SQLite mode, create all tables from models before tests
        Base.metadata.create_all(bind=engine)

        yield engine

        # For SQLite mode, drop all tables after tests
        Base.metadata.drop_all(bind=engine)
        # Remove the SQLite file
        sqlite_file_path = "test_db.sqlite3"
        if os.path.exists(sqlite_file_path):
            os.remove(sqlite_file_path)

        engine.dispose()
        _reset_engine()
        return

    docker_stack = request.getfixturevalue("docker_test_stack")
    restore_state = _configure_postgres(docker_stack["db"])

    engine = get_engine()

    try:
        yield engine
    finally:
        engine.dispose()
        _reset_engine()

        for key, value in restore_state["env"].items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        settings = restore_state["settings_obj"]
        config_module.db_settings = settings
        database_module.db_settings = settings


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Provides a transaction-scoped session for each test function.
    Tests run within transactions and are rolled back on completion,
    ensuring DB state independence between tests.
    """
    # Depend on db_engine fixture and share the initialized engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()

    # Override FastAPI app's DI (get_db) with this test session
    app.dependency_overrides[create_db_session] = lambda: db

    try:
        yield db
    finally:
        db.rollback()  # Rollback all changes
        db.close()
        app.dependency_overrides.pop(create_db_session, None)


@pytest.fixture
async def client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates httpx.AsyncClient configured for database-dependent tests.
    (Depends on db_session fixture to ensure DI override is applied)
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
