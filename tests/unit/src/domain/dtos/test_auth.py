import pytest
from src.domain.dtos.auth import AccessTokenDTO, LoginDTO

pytestmark = pytest.mark.unit


def test_login_dto_fields() -> None:
    dto = LoginDTO(email='x@y.z', password='p')
    assert dto.email == 'x@y.z'
    assert dto.password == 'p'


def test_access_token_dto_defaults() -> None:
    dto = AccessTokenDTO(access_token='abc')
    assert dto.token_type == 'bearer'


def test_access_token_dto_dump() -> None:
    dto = AccessTokenDTO(access_token='t', token_type='custom')
    assert dto.model_dump() == {'access_token': 't', 'token_type': 'custom'}
