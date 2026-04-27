from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

from src.core.config.settings import get_settings


def create_access_token(
    *,
    employee_id: UUID,
    email: str,
    role: str,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        'id': str(employee_id),
        'email': email,
        'role': role,
        'iat': now,
        'exp': now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Valida a assinatura e o prazo (exp) do JWT do fluxo de login.
    Repropaga exceções do PyJWT (ex.: ExpiredSignatureError, InvalidTokenError).
    """
    settings = get_settings()
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
