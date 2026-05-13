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
        raise InvalidOrExpiredTokenException(
            'Access token expired. Call POST /api/v2/login and send the access_token '
            'in the Authorization: Bearer header.'
        ) from e
    except jwt.PyJWTError as e:
        raise InvalidOrExpiredTokenException(
            'Invalid access token. Use the access_token returned by POST /api/v2/login '
            'in the Authorization: Bearer header.'
        ) from e

    sub = payload.get('id')
    if not sub:
        raise InvalidOrExpiredTokenException(
            'Token missing employee identifier. Log in again via POST /api/v2/login.'
        )
    return UUID(str(sub))


CurrentEmployeeIdDep = Annotated[UUID, Depends(get_current_employee_id)]
