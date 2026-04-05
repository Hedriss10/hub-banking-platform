import random
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from src.interface.api.v2 import v2_router
from src.interface.api.v2.controller.employee import EmployeeController
from src.interface.api.v2.dependencies.employee import get_employee_controller


@pytest.fixture
def unique_employee_email() -> str:
    """E-mail único por teste (evita colisão em UNIQUE no Postgres)."""
    return f'john.{uuid.uuid4().hex}@example.com'


@pytest.fixture
def client():
    from src.main import app

    with TestClient(app=app, base_url='http://test') as c:
        yield c


@pytest.fixture
def generate_uuid() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def unique_employee_document() -> str:
    """Documento numérico único (12 dígitos, alinhado aos testes de modelo)."""
    return f'{random.randint(100000000000, 999999999999)}'


@pytest.fixture
def employee_create_dto(unique_employee_email: str, unique_employee_document: str):
    from tests.fixtures.employee_factories import build_employee_create_dto

    return build_employee_create_dto(
        email=unique_employee_email,
        document=unique_employee_document,
    )


@pytest.fixture
def employee_dto():
    from tests.fixtures.employee_factories import build_employee_dto

    return build_employee_dto()


@pytest.fixture
def employee_update_dto():
    from tests.fixtures.employee_factories import build_employee_update_dto

    return build_employee_update_dto()


@pytest.fixture
def random_employee_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_repository_user():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_employee_use_case():
    """Use case mockado para testes do router employee (async)."""
    return AsyncMock()


@pytest.fixture
def v2_test_app() -> FastAPI:
    """
    Inclui todos os módulos em `src/interface/api/v2/routes/`.
    """
    app = FastAPI()
    app.include_router(v2_router, prefix='/api')
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def async_v2_client(
    v2_test_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP assíncrono (httpx) sobre o router v2 completo.
    """
    transport = ASGITransport(app=v2_test_app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.fixture
async def async_employee_client(
    v2_test_app: FastAPI,
    mock_employee_use_case: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP assíncrono sobre `/api/v2/employees` com `EmployeeController` mockado.
    """
    controller = EmployeeController(mock_employee_use_case)

    async def _override_controller() -> EmployeeController:
        return controller

    v2_test_app.dependency_overrides[get_employee_controller] = _override_controller

    transport = ASGITransport(app=v2_test_app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client

    v2_test_app.dependency_overrides.pop(get_employee_controller, None)
