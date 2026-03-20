import os

import pytest

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret-key')
if not os.getenv('SQLALCHEMY_DATABASE_URI'):
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

from src.app import create_app
from src.db.database import db as sqlalchemy_db


@pytest.fixture(scope='session')
def app():
    flask_app = create_app()
    return flask_app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield sqlalchemy_db


@pytest.fixture(scope='function')
def session(app):
    """Transação isolada; use com PostgreSQL e schema real (ver README)."""
    with app.app_context():
        connection = sqlalchemy_db.engine.connect()
        transaction = connection.begin()

        options = dict(bind=connection, binds={})
        scoped = sqlalchemy_db.create_scoped_session(options=options)
        sqlalchemy_db.session = scoped

        yield scoped

        transaction.rollback()
        connection.close()
        scoped.remove()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
