import os
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_engine: Optional[AsyncEngine] = None
_async_session: Optional[async_sessionmaker[AsyncSession]] = None


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/dovvybuddy"
    )


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
