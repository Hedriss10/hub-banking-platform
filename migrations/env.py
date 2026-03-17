import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config.settings import get_settings
from src.infrastructure.database import load_all_models
from src.infrastructure.database.models.base import BaseModel

settings = get_settings()


config = context.config
fileConfig(config.config_file_name)

load_all_models()
target_metadata = BaseModel.metadata


def run_migrations_offline():
    context.configure(
        url=settings.SQLALCHEMY_DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        future=True,
    )
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run_migrations()
