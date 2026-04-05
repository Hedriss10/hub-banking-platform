"""
Testes de integração com PostgreSQL via Testcontainers.

Requisitos: Docker em execução (o Testcontainers sobe um Postgres 15 efêmero).

Executar só integração: `pytest tests/integration -m integration --no-cov`
ou `task test_integration` (após `poetry install`).
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import uuid
from collections.abc import AsyncGenerator, Iterator
from pathlib import Path

import pytest
from pytest_asyncio import fixture as asyncio_fixture
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_session_factory
from testcontainers.postgres import PostgresContainer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _sqlalchemy_asyncpg_url(raw_url: str) -> str:
    """
    Testcontainers PostgresContainer usa driver=psycopg2 por padrão (postgresql+psycopg2://).
    SQLAlchemy async precisa de postgresql+asyncpg://; asyncpg puro aceita só postgresql://.
    """
    if raw_url.startswith('postgresql+asyncpg://'):
        return raw_url
    for prefix in (
        'postgresql+psycopg2://',
        'postgresql+psycopg://',
        'postgresql://',
    ):
        if raw_url.startswith(prefix):
            return 'postgresql+asyncpg://' + raw_url[len(prefix) :]
    msg = f'URI PostgreSQL não suportada para asyncpg/SQLAlchemy: {raw_url!r}'
    raise ValueError(msg)


@pytest.fixture(scope='session')
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer('postgres:15', driver=None) as postgres:
        yield postgres


@pytest.fixture(scope='session')
def integration_database_url(postgres_container: PostgresContainer) -> str:
    return _sqlalchemy_asyncpg_url(postgres_container.get_connection_url())


@pytest.fixture(scope='session')
def integration_database_ready(integration_database_url: str) -> None:
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['SQLALCHEMY_DATABASE_URI'] = integration_database_url

    async def _ensure_schema_and_extensions() -> None:
        import asyncpg

        connect_dsn = integration_database_url.replace(
            'postgresql+asyncpg://', 'postgresql://', 1
        )
        conn = await asyncpg.connect(connect_dsn)
        try:
            await conn.execute('CREATE SCHEMA IF NOT EXISTS "hub-banking-platform";')
            await conn.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')
        finally:
            await conn.close()

    asyncio.run(_ensure_schema_and_extensions())

    env = {
        **os.environ,
        'ENVIRONMENT': 'test',
        'SQLALCHEMY_DATABASE_URI': integration_database_url,
    }
    subprocess.run(
        [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )

    import src.infrastructure.database.session as session_module
    from src.core.config.settings import get_settings

    get_settings.cache_clear()
    session_module.settings = get_settings()
    session_module._engine = None
    session_module._async_session_factory = None


@pytest.fixture
def unique_admin_email() -> str:
    """Email único por teste na tabela admins (constraint UNIQUE em email)."""
    return f'admin.{uuid.uuid4().hex}@example.com'


@pytest.fixture
def integration_client(integration_database_ready: None):
    from fastapi.testclient import TestClient
    from src.main import app

    with TestClient(app=app, base_url='http://test') as c:
        yield c


@asyncio_fixture(scope='function', loop_scope='session')
async def employee_repository_postgres(
    async_session: AsyncSession,
):
    from src.infrastructure.repositories.employee_postgres import (
        EmployeeRepositoryPostgres,
    )

    return EmployeeRepositoryPostgres(async_session)


@asyncio_fixture(scope='function', loop_scope='session')
async def employee_service(employee_repository_postgres):
    from src.domain.service.employee import EmployeeService

    return EmployeeService(employee_repository_postgres)


@asyncio_fixture(scope='function', loop_scope='session')
async def employee_use_case(employee_service):
    from src.domain.use_case.employee import EmployeeUseCase

    return EmployeeUseCase(employee_service)


@asyncio_fixture(scope='function', loop_scope='session')
async def employee_controller(employee_use_case):
    from src.interface.api.v2.controller.employee import EmployeeController

    return EmployeeController(employee_use_case)


@asyncio_fixture(scope='function', loop_scope='session')
async def async_session(
    integration_database_ready: None,
) -> AsyncGenerator[AsyncSession, None]:
    # Mesmo factory da app (expire_on_commit=False).
    # Evita MissingGreenlet ao ler atributos depois do commit.
    # loop_scope=session: um event loop por sessão de testes (compatível com o
    # singleton AsyncEngine); scope=function: sessão SQLAlchemy nova por teste.
    factory = get_session_factory()
    async with factory() as session:
        yield session
