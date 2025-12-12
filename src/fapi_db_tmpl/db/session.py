"""Database session factory and dependency helpers."""

from __future__ import annotations

import threading
from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from fapi_db_tmpl.config import db_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None
_lock = threading.Lock()


def _initialize_factory() -> None:
    """Initialize the global engine and session factory lazily."""
    global _engine, _SessionLocal
    with _lock:
        if _engine is None:
            settings = db_settings
            db_url = settings.DATABASE_URL

            _engine = create_engine(db_url, pool_pre_ping=True)
            _SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=_engine,
            )


def create_db_session() -> Session:
    """Create a new SQLAlchemy session."""
    _initialize_factory()
    assert _SessionLocal is not None
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed afterwards."""
    session = create_db_session()
    try:
        yield session
    finally:
        session.close()


def get_engine() -> Engine:
    """Expose the underlying Engine for migrations or low-level access."""
    _initialize_factory()
    assert _engine is not None
    return _engine


__all__ = ["create_db_session", "get_db", "get_engine"]

