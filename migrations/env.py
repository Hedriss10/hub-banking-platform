import os
from logging.config import fileConfig

from alembic import context
from src.app import create_app
from src.db.database import db

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import src.models.models  # noqa: F401 — registra tabelas em db.metadata


def run_migrations_offline() -> None:
    url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not url:
        raise RuntimeError('Defina SQLALCHEMY_DATABASE_URI para migrations offline.')
    context.configure(
        url=url,
        target_metadata=db.metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    flask_app = create_app()
    with flask_app.app_context():
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=db.metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
