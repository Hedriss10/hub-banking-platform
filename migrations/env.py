from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv

from src.app import create_app
from src.database import load_all_models
from src.database.database import db

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_all_models()


def run_migrations_online() -> None:
    """Sempre com banco ligado: usa `create_app()` e a engine do Flask-SQLAlchemy."""
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
    raise RuntimeError(
        'Este projeto usa apenas migrations online (Postgres em execução). '
        'Defina SQLALCHEMY_DATABASE_URI, suba o banco e execute: alembic upgrade head'
    )

run_migrations_online()
