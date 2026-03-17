from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.core.config.settings import get_settings
from src.core.exceptions.custom import DatabaseException

settings = get_settings()

_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """Cria a engine async apenas uma vez"""
    global _engine

    if _engine is None:
        database_uri = settings.SQLALCHEMY_DATABASE_URI
        if database_uri is None:
            raise ValueError('SQLALCHEMY_DATABASE_URI must be set')
        _engine = create_async_engine(
            database_uri,
            echo=False,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_TIMEOUT,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Cria o session factory async uma vez"""
    global _async_session_factory

    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )

    return _async_session_factory


async def get_session(
    verify_connection: bool = True,
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency padrão"""
    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            if verify_connection:
                await session.connection()

            yield session

        except ConnectionRefusedError as error:
            raise DatabaseException(
                f'Erro ao conectar ao banco de dados: {error}'
            ) from error


async def get_unverified_session() -> AsyncGenerator[AsyncSession, None]:
    """Sem verificação de conexão"""
    async for session in get_session(verify_connection=False):
        yield session


async def get_verified_session() -> AsyncGenerator[AsyncSession, None]:
    """Com verificação de conexão"""
    async for session in get_session(verify_connection=True):
        yield session
