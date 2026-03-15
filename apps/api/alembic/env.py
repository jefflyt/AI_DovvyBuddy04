import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context
from app.infrastructure.db import models  # noqa: F401
from app.infrastructure.db.base import Base

# Load environment variables from project root .env.local
# alembic/env.py is in apps/api/alembic/, so go up 4 levels to project root
project_root = Path(__file__).resolve().parent.parent.parent.parent
env_path = project_root / ".env.local"
load_dotenv(dotenv_path=env_path)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with environment variable (convert asyncpg to psycopg2)
database_url = os.getenv("DATABASE_URL", "")
if database_url:
    # Alembic needs synchronous driver (psycopg2), not asyncpg
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    # Fix SSL parameter format for psycopg2 (ssl=require -> sslmode=require)
    sync_url = sync_url.replace("ssl=require", "sslmode=require")
    config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to Base.metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    context.run_migrations()
else:
    run_migrations_online()
