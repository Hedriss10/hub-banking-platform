from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from src.infrastructure.database.utils.status_code import (
    PostgresErrorCode,
    is_unique_violation,
)

pytestmark = pytest.mark.unit


def test_is_unique_violation_false_when_orig_none() -> None:
    err = MagicMock(spec=IntegrityError)
    err.orig = None
    assert is_unique_violation(err) is False


def test_is_unique_violation_true_pgcode() -> None:
    err = MagicMock(spec=IntegrityError)
    err.orig = MagicMock()
    err.orig.pgcode = PostgresErrorCode.UNIQUE_VIOLATION
    err.orig.sqlstate = None
    assert is_unique_violation(err) is True


def test_is_unique_violation_true_sqlstate() -> None:
    err = MagicMock(spec=IntegrityError)
    err.orig = MagicMock()
    err.orig.pgcode = None
    err.orig.sqlstate = PostgresErrorCode.UNIQUE_VIOLATION
    assert is_unique_violation(err) is True


def test_is_unique_violation_false_other_code() -> None:
    err = MagicMock(spec=IntegrityError)
    err.orig = MagicMock()
    err.orig.pgcode = '23503'
    err.orig.sqlstate = None
    assert is_unique_violation(err) is False
