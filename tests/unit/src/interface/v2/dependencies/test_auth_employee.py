from uuid import uuid4

import jwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials
from src.domain.exceptions.auth import InvalidOrExpiredTokenException
from src.interface.api.v2.dependencies.common import auth_employee as auth_mod
from src.interface.api.v2.dependencies.common.auth_employee import (
    get_current_employee_id,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_current_employee_id_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uid = uuid4()
    monkeypatch.setattr(
        auth_mod,
        'decode_access_token',
        lambda _t: {'id': str(uid), 'email': 'a@b.com'},
    )
    creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials='tok')
    out = await get_current_employee_id(creds)
    assert out == uid


@pytest.mark.asyncio
async def test_get_current_employee_id_expired(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(_t: str) -> None:
        raise jwt.ExpiredSignatureError('expired')

    monkeypatch.setattr(auth_mod, 'decode_access_token', _raise)
    creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials='tok')
    with pytest.raises(InvalidOrExpiredTokenException, match='Access token expired'):
        await get_current_employee_id(creds)


@pytest.mark.asyncio
async def test_get_current_employee_id_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(_t: str) -> None:
        raise jwt.InvalidTokenError('bad')

    monkeypatch.setattr(auth_mod, 'decode_access_token', _raise)
    creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials='tok')
    with pytest.raises(InvalidOrExpiredTokenException, match='Invalid access token'):
        await get_current_employee_id(creds)


@pytest.mark.asyncio
async def test_get_current_employee_id_missing_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auth_mod, 'decode_access_token', lambda _t: {})
    creds = HTTPAuthorizationCredentials(scheme='Bearer', credentials='tok')
    with pytest.raises(InvalidOrExpiredTokenException, match='employee identifier'):
        await get_current_employee_id(creds)
