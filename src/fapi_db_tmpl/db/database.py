import threading
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from fapi_db_tmpl.config import db_settings

# --- Lazy Initialization for Database Engine and Session Factory ---

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None
_lock = threading.Lock()


def _initialize_factory() -> None:
    """
    Lazy initializer for the database engine and session factory.
    This prevents settings from being loaded at import time and is thread-safe.
    Uses PostgreSQL as the single database backend.
    """
    global _engine, _SessionLocal
    with _lock:
        if _engine is None:
            settings = db_settings

            db_url = settings.DATABASE_URL

            # PostgreSQL engine used for all environments (tests, dev, prod)
            _engine = create_engine(db_url, pool_pre_ping=True)

            _SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=_engine
            )


def create_db_session() -> Session:
    """
    Creates a new SQLAlchemy session.
    For direct use in places like middleware or background tasks.
    """
    _initialize_factory()
    assert _SessionLocal is not None
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session and ensures it's closed.
    """
    session = create_db_session()
    try:
        yield session
    finally:
        session.close()


# --- Declarative Base for Models ---

Base = declarative_base()


# Make Base and Engine accessible to external modules (especially test fixtures)
def get_engine() -> Engine:
    _initialize_factory()
    assert _engine is not None
    return _engine
