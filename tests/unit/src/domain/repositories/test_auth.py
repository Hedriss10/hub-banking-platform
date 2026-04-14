import pytest
from src.domain.repositories.auth import AuthRepository
from src.infrastructure.repositories.auth_postgres import AuthPostgresRepository

pytestmark = pytest.mark.unit


def test_auth_repository_is_abstract() -> None:
    with pytest.raises(TypeError):
        AuthRepository()


def test_auth_postgres_repository_implements_auth_repository() -> None:
    assert issubclass(AuthPostgresRepository, AuthRepository)
