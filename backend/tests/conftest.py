import asyncio

import pytest

from app.db.session import init_db


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    # Initialize DB engine (uses DATABASE_URL from env or .env)
    await init_db()
    yield
