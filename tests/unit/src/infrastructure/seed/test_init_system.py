from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import src.infrastructure.seed.init_system as init_system_module
from src.infrastructure.database.models.admin import Admin
from src.infrastructure.database.models.common.role import RoleStatus
from src.infrastructure.database.models.employee import Employee
from src.infrastructure.seed.init_system import (
    DEV_USER_EMAIL,
    _ensure_dev_admin,
    _ensure_dev_employee,
    init_system,
    main,
    run_init_system,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def password_hash() -> str:
    return 'hashed-password'


@pytest.mark.asyncio
async def test_ensure_dev_employee_creates_user(
    mock_session: AsyncMock,
    password_hash: str,
) -> None:
    mock_session.scalar = AsyncMock(return_value=None)

    created = await _ensure_dev_employee(mock_session, password_hash)

    assert created is True
    mock_session.add.assert_called_once()
    employee = mock_session.add.call_args.args[0]
    assert isinstance(employee, Employee)
    assert employee.email == DEV_USER_EMAIL
    assert employee.role == RoleStatus.ADMIN


@pytest.mark.asyncio
async def test_ensure_dev_employee_skips_when_exists(
    mock_session: AsyncMock,
    password_hash: str,
) -> None:
    mock_session.scalar = AsyncMock(return_value=MagicMock())

    created = await _ensure_dev_employee(mock_session, password_hash)

    assert created is False
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_dev_admin_creates_user(
    mock_session: AsyncMock,
    password_hash: str,
) -> None:
    mock_session.scalar = AsyncMock(return_value=None)

    created = await _ensure_dev_admin(mock_session, password_hash)

    assert created is True
    mock_session.add.assert_called_once()
    admin = mock_session.add.call_args.args[0]
    assert isinstance(admin, Admin)
    assert admin.email == DEV_USER_EMAIL
    assert admin.role == RoleStatus.ADMIN
    assert admin.password == password_hash


@pytest.mark.asyncio
async def test_ensure_dev_admin_skips_when_exists(
    mock_session: AsyncMock,
    password_hash: str,
) -> None:
    mock_session.scalar = AsyncMock(return_value=MagicMock())

    created = await _ensure_dev_admin(mock_session, password_hash)

    assert created is False
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_init_system_creates_employee_and_admin(
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.scalar = AsyncMock(side_effect=[None, None])
    monkeypatch.setattr(
        init_system_module,
        'hash_password',
        lambda _password: 'hashed-password',
    )

    await init_system(mock_session)

    added = [call.args[0] for call in mock_session.add.call_args_list]
    assert {type(record) for record in added} == {Employee, Admin}
    assert mock_session.scalar.await_count == len(added)
    employee = next(record for record in added if isinstance(record, Employee))
    admin = next(record for record in added if isinstance(record, Admin))
    assert employee.password == 'hashed-password'
    assert admin.password == 'hashed-password'
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_system_skips_when_both_exist(
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.scalar = AsyncMock(side_effect=[MagicMock(), MagicMock()])
    monkeypatch.setattr(
        init_system_module,
        'hash_password',
        lambda _password: 'hashed-password',
    )

    await init_system(mock_session)

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_init_system_creates_only_admin_when_employee_exists(
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.scalar = AsyncMock(side_effect=[MagicMock(), None])
    monkeypatch.setattr(
        init_system_module,
        'hash_password',
        lambda _password: 'hashed-password',
    )

    await init_system(mock_session)

    mock_session.add.assert_called_once()
    assert isinstance(mock_session.add.call_args.args[0], Admin)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_system_creates_only_employee_when_admin_exists(
    mock_session: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_session.scalar = AsyncMock(side_effect=[None, MagicMock()])
    monkeypatch.setattr(
        init_system_module,
        'hash_password',
        lambda _password: 'hashed-password',
    )

    await init_system(mock_session)

    mock_session.add.assert_called_once()
    assert isinstance(mock_session.add.call_args.args[0], Employee)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_init_system() -> None:
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.scalar = AsyncMock(side_effect=[None, None])

    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

    with patch.object(
        init_system_module,
        'get_session_factory',
        return_value=mock_factory,
    ):
        with patch.object(
            init_system_module,
            'hash_password',
            return_value='hashed-password',
        ):
            await run_init_system()

    mock_session.commit.assert_awaited_once()


def test_main() -> None:
    async def _noop() -> None:
        return None

    with patch.object(init_system_module.asyncio, 'run') as mock_run:
        with patch.object(init_system_module, 'run_init_system', new=_noop):
            main()

    mock_run.assert_called_once()
