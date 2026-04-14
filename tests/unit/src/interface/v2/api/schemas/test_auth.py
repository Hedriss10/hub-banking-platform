import pytest
from pydantic import ValidationError
from src.interface.api.v2.schemas.auth import LoginRequestSchema, LoginResponseSchema

pytestmark = pytest.mark.unit


def test_login_request_schema_accepts_email_and_password() -> None:
    schema = LoginRequestSchema(email='user@example.com', password='secret123')
    assert schema.email == 'user@example.com'
    assert schema.password == 'secret123'


def test_login_request_schema_model_dump() -> None:
    schema = LoginRequestSchema(email='a@b.co', password='x')
    dumped = schema.model_dump()
    assert dumped == {'email': 'a@b.co', 'password': 'x'}


def test_login_request_schema_requires_email() -> None:
    with pytest.raises(ValidationError) as exc_info:
        LoginRequestSchema(password='only-password')
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('email',) for e in errors)


def test_login_request_schema_requires_password() -> None:
    with pytest.raises(ValidationError) as exc_info:
        LoginRequestSchema(email='only@email.com')
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('password',) for e in errors)


def test_login_response_schema_requires_access_token() -> None:
    with pytest.raises(ValidationError) as exc_info:
        LoginResponseSchema()
    errors = exc_info.value.errors()
    assert any(e['loc'] == ('access_token',) for e in errors)


def test_login_response_schema_default_token_type_is_bearer() -> None:
    schema = LoginResponseSchema(access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.x')
    assert schema.token_type == 'bearer'


def test_login_response_schema_accepts_custom_token_type() -> None:
    schema = LoginResponseSchema(access_token='t', token_type='Bearer')
    assert schema.token_type == 'Bearer'


def test_login_response_schema_model_dump_includes_defaults() -> None:
    schema = LoginResponseSchema(access_token='abc')
    assert schema.model_dump() == {'access_token': 'abc', 'token_type': 'bearer'}
