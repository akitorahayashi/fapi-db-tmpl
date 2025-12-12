"""Database-specific test fixtures backed by PostgreSQL."""

from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def db_url() -> Generator[str, None, None]:
    """Provide a PostgreSQL URL using a Testcontainers-managed database."""
    with PostgresContainer("postgres:16-alpine") as pg:
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
    from src.fapi_db_tmpl.db.database import create_db_session

    app.dependency_overrides[create_db_session] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
