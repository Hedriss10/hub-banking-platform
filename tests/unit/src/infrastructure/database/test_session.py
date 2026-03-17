from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import src.infrastructure.database.session as session_module
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from src.core.exceptions.custom import DatabaseException

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.SQLALCHEMY_DATABASE_URI = 'asyncpg://test'
    settings.DATABASE_POOL_SIZE = 5
    settings.DATABASE_MAX_OVERFLOW = 10
    settings.DATABASE_TIMEOUT = 30
    return settings


@pytest.fixture(autouse=True)
def reset_globals(mock_settings):
    # Reset globals and set mock_settings before each test
    session_module._engine = None
    session_module._async_session_factory = None
    original_settings = session_module.settings
    session_module.settings = mock_settings
    yield
    session_module._engine = None
    session_module._async_session_factory = None
    session_module.settings = original_settings  # Restore original if needed


@patch('src.infrastructure.database.session.create_async_engine')
def test_get_engine_creates_once(mock_create_engine):
    # Arrange: Mock create_async_engine
    mock_engine = MagicMock(spec=AsyncEngine)
    mock_create_engine.return_value = mock_engine

    # Act: Call twice
    engine1 = session_module.get_engine()
    engine2 = session_module.get_engine()

    # Assert: Created only once with correct params
    mock_create_engine.assert_called_once_with(
        session_module.settings.SQLALCHEMY_DATABASE_URI,
        echo=False,
        pool_size=session_module.settings.DATABASE_POOL_SIZE,
        max_overflow=session_module.settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=session_module.settings.DATABASE_TIMEOUT,
        pool_pre_ping=True,
    )
    assert engine1 == mock_engine
    assert engine2 == engine1


def test_get_engine_raises_when_database_uri_is_none(mock_settings):
    """get_engine deve lançar ValueError quando SQLALCHEMY_DATABASE_URI for None."""
    mock_settings.SQLALCHEMY_DATABASE_URI = None

    with pytest.raises(ValueError, match='SQLALCHEMY_DATABASE_URI must be set'):
        session_module.get_engine()


@patch('src.infrastructure.database.session.async_sessionmaker')
@patch('src.infrastructure.database.session.get_engine')
def test_get_session_factory_creates_once(mock_get_engine, mock_sessionmaker):
    # Arrange: Mock get_engine and async_sessionmaker
    mock_engine = MagicMock(spec=AsyncEngine)
    mock_get_engine.return_value = mock_engine
    mock_factory = MagicMock(spec=async_sessionmaker)
    mock_sessionmaker.return_value = mock_factory

    # Act: Call twice
    factory1 = session_module.get_session_factory()
    factory2 = session_module.get_session_factory()

    # Assert: Created only once with bind correct
    mock_sessionmaker.assert_called_once_with(
        bind=mock_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    assert factory1 == mock_factory
    assert factory2 == factory1


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session_factory')
async def test_get_session_verified_success(mock_get_factory):
    # Arrange: Mock factory and session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.connection.return_value = None  # Success on connection
    mock_factory_instance = MagicMock()
    mock_factory_instance.__aenter__.return_value = mock_session
    mock_factory_instance.__aexit__.return_value = None
    mock_get_factory.return_value = lambda: mock_factory_instance

    # Act: Use the generator
    async for session in session_module.get_session(verify_connection=True):
        assert session == mock_session
        mock_session.connection.assert_awaited_once()  # Verifies connection


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session_factory')
async def test_get_session_unverified_success(mock_get_factory):
    # Arrange: Similar, but no verify
    mock_session = AsyncMock(spec=AsyncSession)
    mock_factory_instance = MagicMock()
    mock_factory_instance.__aenter__.return_value = mock_session
    mock_factory_instance.__aexit__.return_value = None
    mock_get_factory.return_value = lambda: mock_factory_instance

    # Act
    async for session in session_module.get_session(verify_connection=False):
        assert session == mock_session
        mock_session.connection.assert_not_called()  # No verification


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session_factory')
async def test_get_session_connection_refused(mock_get_factory):
    # Arrange: Simulate ConnectionRefusedError
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.connection.side_effect = ConnectionRefusedError('Connection refused')
    mock_factory_instance = MagicMock()
    mock_factory_instance.__aenter__.return_value = mock_session
    mock_factory_instance.__aexit__.return_value = None
    mock_get_factory.return_value = lambda: mock_factory_instance

    # Act & Assert: Raises DatabaseException
    with pytest.raises(
        DatabaseException,
        match='Erro ao conectar ao banco de dados: Connection refused',
    ):
        async for _ in session_module.get_session(verify_connection=True):
            pass


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session_factory')
async def test_get_session_other_exception(mock_get_factory):
    # Arrange: Simulate other exception in try block
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.connection.side_effect = ValueError('Other error')
    mock_factory_instance = MagicMock()
    mock_factory_instance.__aenter__.return_value = mock_session
    mock_factory_instance.__aexit__.return_value = None
    mock_get_factory.return_value = lambda: mock_factory_instance

    with pytest.raises(ValueError, match='Other error'):
        async for _ in session_module.get_session(verify_connection=True):
            pass


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session')
async def test_get_unverified_session(mock_get_session):
    # Arrange: Mock get_session
    mock_gen = AsyncMock()
    mock_get_session.return_value = mock_gen

    # Act
    gen = session_module.get_unverified_session()
    async for session in gen:
        pass

    # Assert: Calls with verify=False
    mock_get_session.assert_called_once_with(verify_connection=False)


@pytest.mark.asyncio
@patch('src.infrastructure.database.session.get_session')
async def test_get_verified_session(mock_get_session):
    # Arrange: Similar
    mock_gen = AsyncMock()
    mock_get_session.return_value = mock_gen

    # Act
    gen = session_module.get_verified_session()
    async for session in gen:
        pass

    # Assert: Calls with verify=True
    mock_get_session.assert_called_once_with(verify_connection=True)


@pytest.mark.asyncio
async def test_get_unverified_session_yield():
    # Arrange: Mock get_session to return an async generator yielding a mock session
    mock_session = AsyncMock(spec=AsyncSession)

    async def mock_inner_gen():
        yield mock_session

    with patch('src.infrastructure.database.session.get_session') as mock_get_session:
        mock_get_session.return_value = mock_inner_gen()

        # Act: Get the generator and consume it
        gen = session_module.get_unverified_session()
        yielded_sessions = []
        async for session in gen:
            yielded_sessions.append(session)

        # Assert: Called with False, and yields the session
        mock_get_session.assert_called_once_with(verify_connection=False)
        assert len(yielded_sessions) == 1
        assert yielded_sessions[0] == mock_session


@pytest.mark.asyncio
async def test_get_verified_session_yield():
    # Arrange: Similar for verified
    mock_session = AsyncMock(spec=AsyncSession)

    async def mock_inner_gen():
        yield mock_session

    with patch('src.infrastructure.database.session.get_session') as mock_get_session:
        mock_get_session.return_value = mock_inner_gen()

        # Act: Get the generator and consume it
        gen = session_module.get_verified_session()
        yielded_sessions = []
        async for session in gen:
            yielded_sessions.append(session)

        # Assert: Called with True, and yields the session
        mock_get_session.assert_called_once_with(verify_connection=True)
        assert len(yielded_sessions) == 1
        assert yielded_sessions[0] == mock_session
