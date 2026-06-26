import asyncio
import os
import pytest

# Ensure it is set BEFORE importing anything that might read settings
os.environ["GEMINI_API_KEY"] = "dummy_key_from_conftest"

from app.infrastructure.db.session import init_db


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
