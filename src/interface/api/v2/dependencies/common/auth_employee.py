from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.exceptions.auth import InvalidOrExpiredTokenException
from src.infrastructure.utils.jwt_token import decode_access_token

_http_bearer = HTTPBearer()


async def get_current_employee_id(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
) -> UUID:
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError as e:
        raise InvalidOrExpiredTokenException('O token de acesso expirou') from e
    except jwt.PyJWTError as e:
        raise InvalidOrExpiredTokenException('Token de acesso inválido') from e

    sub = payload.get('id')
    if not sub:
        raise InvalidOrExpiredTokenException('Token sem identificador de funcionário')
    return UUID(str(sub))


CurrentEmployeeIdDep = Annotated[UUID, Depends(get_current_employee_id)]
