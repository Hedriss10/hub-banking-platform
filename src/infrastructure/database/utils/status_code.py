from enum import StrEnum

from sqlalchemy.exc import IntegrityError


class PostgresErrorCode(StrEnum):
    UNIQUE_VIOLATION = '23505'
    FOREIGN_KEY_VIOLATION = '23503'
    NOT_NULL_VIOLATION = '23502'
    CHECK_VIOLATION = '23514'


def is_unique_violation(error: IntegrityError) -> bool:
    orig = error.orig
    if orig is None:
        return False
    code = getattr(orig, 'pgcode', None) or getattr(orig, 'sqlstate', None)
    return code == PostgresErrorCode.UNIQUE_VIOLATION
