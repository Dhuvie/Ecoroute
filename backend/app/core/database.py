"""
EcoRoute Backend - Database Setup
=================================

SQLAlchemy 2.0 declarative base + session factory.

Author : EcoRoute Backend Team
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Annotated

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

logger = logging.getLogger("ecoroute.database")

# SQLite needs special args for thread-safety under FastAPI
_db_url = settings.safe_database_url
connect_args = (
    {"check_same_thread": False}
    if _db_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    _db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)

Base = declarative_base()


def init_db() -> None:
    """Create all tables. Safe to call on every startup."""
    # Ensure SQLite directory exists if using SQLite
    if _db_url.startswith("sqlite:///"):
        db_path = _db_url.split("sqlite:///", 1)[1]
        from pathlib import Path
        try:
            Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning("Could not create database directory: %s", e)

    # Import models so they register with Base.metadata
    from .. import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised at %s", settings.database_url)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Convenience type hint for path-operation dependencies
DbSession = Annotated[Session, "depends(get_db)"]
