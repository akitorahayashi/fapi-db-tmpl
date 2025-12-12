"""ORM base model definitions for fapi-db-tmpl."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models."""

    pass


__all__ = ["Base"]

