"""Database-specific test fixtures."""

import os
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def db_url() -> Generator[str, None, None]:
    use_sqlite = os.environ.get("USE_SQLITE", "true").lower() == "true"
    if use_sqlite:
        sqlite_url = "sqlite:///./test_db.sqlite3"
        yield sqlite_url
        if os.path.exists("./test_db.sqlite3"):
            os.remove("./test_db.sqlite3")
    else:
        from testcontainers.postgres import PostgresContainer

        with PostgresContainer("postgres:16-alpine") as pg:
            # If needed, run alembic migrations here
            async_url = (
                make_url(pg.get_connection_url())
                .render_as_string(hide_password=False)
                .replace("psycopg2", "psycopg")
            )
            yield async_url


@pytest.fixture
async def db_session(db_url: str) -> AsyncGenerator[Session, None]:
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
async def client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    from src.fapi_db_tmpl.api.main import app

    # If needed, override DB session dependency here
    from src.fapi_db_tmpl.db.database import create_db_session

    app.dependency_overrides[create_db_session] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
