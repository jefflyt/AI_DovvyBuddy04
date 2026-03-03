from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_engine: Optional[AsyncEngine] = None
_async_session: Optional[async_sessionmaker[AsyncSession]] = None
_sync_engine: Optional[Engine] = None
_sync_session_factory = None


def get_database_url() -> str:
    """Get async database URL (converts postgresql:// to postgresql+asyncpg://)."""
    url = settings.database_url or (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dovvybuddy"
    )
    # Ensure asyncpg driver for async operations
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Convert sslmode to ssl for asyncpg
    url = url.replace("?sslmode=require", "?ssl=require")
    url = url.replace("&sslmode=require", "&ssl=require")
    # Remove channel_binding (not supported by asyncpg)
    url = url.replace("&channel_binding=require", "")
    url = url.replace("?channel_binding=require", "")
    return url


def get_sync_database_url() -> str:
    """Get synchronous database URL (replaces asyncpg with psycopg2)."""
    url = settings.database_url or (
        "postgresql://postgres:postgres@localhost:5432/dovvybuddy"
    )
    # Ensure plain postgresql:// for sync operations
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


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


async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes to get database session."""
    async_session = get_session()
    async with async_session() as session:
        yield session


async def reset_db_session_state() -> None:
    """Reset cached DB engines/session makers (useful for tests)."""
    global _engine, _async_session, _sync_engine, _sync_session_factory

    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _async_session = None

    if _sync_engine is not None:
        _sync_engine.dispose()
    _sync_engine = None
    _sync_session_factory = None
