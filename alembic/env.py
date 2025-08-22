from __future__ import annotations

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add project root to the path to ensure modules are found
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import settings
from database import Base
# Import all models here so that Alembic's 'autogenerate'
# feature can detect them.
import user  # noqa: F401
import patient  # noqa: F401
import visit  # noqa: F401
import prescription  # noqa: F401
import consent  # noqa: F401
import lab  # noqa: F401
import product  # noqa: F401
import stock  # noqa: F401
import pos  # noqa: F401
import audit  # noqa: F401
import medicine  # noqa: F401
import spectacle  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.sync_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.sync_database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()