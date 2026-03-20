"""
Sessão síncrona alinhada com Flask-SQLAlchemy.

- Com `app_context` ativo: use `get_db_session()` ou `session_scope()` (usa `db.session`).
- Fora da app (scripts): use `standalone_session(url=...)` com a mesma URI do `.env`.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from flask import current_app, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.database import db
from src.database.uri import ensure_sync_postgres_uri


def get_db_session() -> Session:
    """Sessão do Flask-SQLAlchemy; exige `application context` (request ou `with app.app_context()`)."""
    if not has_app_context():
        raise RuntimeError(
            'get_db_session() precisa de application context. '
            'Use `with app.app_context():` ou acesse dentro de um request.'
        )
    return db.session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Transação na sessão da app: commit se não houver exceção, senão rollback.
    Exige application context.
    """
    if not has_app_context():
        raise RuntimeError('session_scope() precisa de application context.')
    sess = db.session
    try:
        yield sess
        sess.commit()
    except Exception:
        sess.rollback()
        raise


@contextmanager
def standalone_session(
    database_url: Optional[str] = None,
) -> Generator[Session, None, None]:
    """
    Sessão independente (CLI, jobs) sem Flask. Fecha engine ao sair.
    """
    url = database_url or os.getenv('SQLALCHEMY_DATABASE_URI')
    if not url:
        raise RuntimeError(
            'Defina SQLALCHEMY_DATABASE_URI no ambiente ou passe database_url=.'
        )
    url = ensure_sync_postgres_uri(url) or url
    engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
