import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base
from app.core.config import settings
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.risk import Risk  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.risk_analysis  import RiskAnalysis  # noqa: F401
from app.models.answer import Answer  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Функция, которая выполняется внутри синхронного контекста.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Асинхронная обертка для запуска миграций.
    Создает асинхронный engine и передает синхронное соединение.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# Определяем режим: online (подключение к БД) или offline (генерация SQL)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()