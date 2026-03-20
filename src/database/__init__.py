import importlib
import pkgutil
from pathlib import Path

from src.database.database import db
from src.database.session import (
    get_db_session,
    session_scope,
    standalone_session,
)
from src.database.uri import ensure_sync_postgres_uri

__all__ = [
    'db',
    'ensure_sync_postgres_uri',
    'get_db_session',
    'load_all_models',
    'session_scope',
    'standalone_session',
]


def load_all_models() -> None:
    """Importa submódulos de `src.models` para registrar metadados/tabelas."""
    models_dir = Path(__file__).resolve().parent.parent / 'models'
    if not models_dir.is_dir():
        return
    for info in pkgutil.walk_packages(
        path=[str(models_dir)],
        prefix='src.models.',
    ):
        importlib.import_module(info.name)
