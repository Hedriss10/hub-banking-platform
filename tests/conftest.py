import random
import uuid
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.interface.api.v2 import v2_router
from src.interface.api.v2.controller.employee import EmployeeController
from src.interface.api.v2.dependencies.employee import get_employee_controller

from tests.async_http import async_client_for_app


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
def v2_test_app() -> Generator[FastAPI, None, None]:
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
    async with async_client_for_app(v2_test_app) as client:
        yield client


@pytest.fixture
def mock_employee_use_case() -> AsyncMock:
    """Use case mockado para testes do router employee (async)."""
    return AsyncMock()


@pytest.fixture
async def async_employee_client(
    v2_test_app: FastAPI,
    mock_employee_use_case: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Mesmo transporte que `async_v2_client`, com override do `EmployeeController`."""
    controller = EmployeeController(mock_employee_use_case)

    async def _override_controller() -> EmployeeController:
        return controller

    v2_test_app.dependency_overrides[get_employee_controller] = _override_controller

    async with async_client_for_app(v2_test_app) as client:
        yield client

    v2_test_app.dependency_overrides.pop(get_employee_controller, None)


@pytest.fixture
def mock_auth_use_case() -> AsyncMock:
    """Use case mockado para testes do router de login (async)."""
    return AsyncMock()


@pytest.fixture
async def async_auth_client(
    v2_test_app: FastAPI,
    mock_auth_use_case: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Cliente v2 com override do `AuthController` (use case mockado)."""
    from src.interface.api.v2.controller.auth import AuthController
    from src.interface.api.v2.dependencies.auth import get_auth_controller

    controller = AuthController(mock_auth_use_case)

    async def _override_controller() -> AuthController:
        return controller

    v2_test_app.dependency_overrides[get_auth_controller] = _override_controller

    async with async_client_for_app(v2_test_app) as client:
        yield client

    v2_test_app.dependency_overrides.pop(get_auth_controller, None)


@pytest.fixture
def mock_bankers_use_case() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def async_bankers_client(
    v2_test_app: FastAPI,
    mock_bankers_use_case: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    from src.interface.api.v2.controller.bankers import BankersController
    from src.interface.api.v2.dependencies.bankers import get_bankers_controller
    from src.interface.api.v2.dependencies.common.auth_employee import (
        get_current_employee_id,
    )

    controller = BankersController(mock_bankers_use_case)

    async def _override_bankers() -> BankersController:
        return controller

    async def _override_employee() -> UUID:
        return uuid.uuid4()

    v2_test_app.dependency_overrides[get_bankers_controller] = _override_bankers
    v2_test_app.dependency_overrides[get_current_employee_id] = _override_employee

    async with async_client_for_app(v2_test_app) as client:
        yield client

    v2_test_app.dependency_overrides.pop(get_bankers_controller, None)
    v2_test_app.dependency_overrides.pop(get_current_employee_id, None)


@pytest.fixture
def mock_financial_agreements_use_case() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def async_financial_agreements_client(
    v2_test_app: FastAPI,
    mock_financial_agreements_use_case: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    from src.interface.api.v2.controller.financial_agreements import (
        FinancialAgreementsController,
    )
    from src.interface.api.v2.dependencies.common.auth_employee import (
        get_current_employee_id,
    )
    from src.interface.api.v2.dependencies.financial_agreements import (
        get_financial_agreements_controller,
    )

    controller = FinancialAgreementsController(mock_financial_agreements_use_case)

    async def _override_controller() -> FinancialAgreementsController:
        return controller

    async def _override_employee() -> UUID:
        return uuid.uuid4()

    v2_test_app.dependency_overrides[get_financial_agreements_controller] = (
        _override_controller
    )
    v2_test_app.dependency_overrides[get_current_employee_id] = _override_employee

    async with async_client_for_app(v2_test_app) as client:
        yield client

    v2_test_app.dependency_overrides.pop(get_financial_agreements_controller, None)
    v2_test_app.dependency_overrides.pop(get_current_employee_id, None)
