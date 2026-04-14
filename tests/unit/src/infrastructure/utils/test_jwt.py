"""Testes de `create_access_token` (PyJWT + settings)."""

from uuid import uuid4

import jwt
import pytest
from src.core.config.settings import Settings
from src.infrastructure.utils import jwt_token as jwt_token_module

pytestmark = pytest.mark.unit


def _settings_jwt() -> Settings:
    return Settings(
        SQLALCHEMY_DATABASE_URI=(
            'postgresql+asyncpg://u:p@localhost:5432/hub-banking-platform'
        ),
        JWT_SECRET='s' * 32,
        JWT_ALGORITHM='HS256',
        JWT_EXPIRE_MINUTES=60,
    )


def test_create_access_token_encodes_and_decodes_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _settings_jwt()
    monkeypatch.setattr(jwt_token_module, 'get_settings', lambda: settings)

    eid = uuid4()
    token = jwt_token_module.create_access_token(
        employee_id=eid,
        email='user@example.com',
        role='ADMIN',
    )

    decoded = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert decoded['id'] == str(eid)
    assert decoded['email'] == 'user@example.com'
    assert decoded['role'] == 'ADMIN'
    assert 'exp' in decoded
    assert 'iat' in decoded
