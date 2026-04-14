from datetime import datetime, timedelta, timezone
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
