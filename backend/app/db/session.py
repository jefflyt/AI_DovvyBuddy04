import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

_engine: Optional[AsyncEngine] = None
_async_session: Optional[async_sessionmaker[AsyncSession]] = None
_sync_engine = None
_sync_session_factory = None


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/dovvybuddy"
    )


def get_sync_database_url() -> str:
    """Get synchronous database URL (replaces asyncpg with psycopg2)."""
    url = get_database_url()
    # Replace asyncpg with psycopg2 for synchronous connections
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def init_db() -> None:
    global _engine, _async_session
    if _engine is None:
        database_url = get_database_url()
        _engine = create_async_engine(database_url, future=True, echo=False)
        _async_session = async_sessionmaker(_engine, expire_on_commit=False)


def get_session() -> async_sessionmaker[AsyncSession]:
    if _async_session is None:
        raise RuntimeError("DB not initialized; call init_db() first")
    return _async_session


def get_sync_engine():
    """Get or create synchronous engine for scripts."""
    global _sync_engine
    if _sync_engine is None:
        database_url = get_sync_database_url()
        _sync_engine = create_engine(database_url, echo=False)
    return _sync_engine


def SessionLocal() -> Session:
    """Create a new synchronous database session for scripts."""
    global _sync_session_factory
    if _sync_session_factory is None:
        engine = get_sync_engine()
        _sync_session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return _sync_session_factory()
