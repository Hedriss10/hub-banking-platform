"""Tests for loan-operation domain exceptions."""

import pytest
from src.domain.exceptions.loan_operation import LoanOperationNotFoundException

pytestmark = pytest.mark.unit


def test_loan_operation_not_found_default_message() -> None:
    exc = LoanOperationNotFoundException()
    assert str(exc) == 'Loan operation not found'
    assert exc.code == 'LOAN_OPERATION_NOT_FOUND'


def test_loan_operation_not_found_custom_message() -> None:
    exc = LoanOperationNotFoundException(message='Custom')
    assert str(exc) == 'Custom'
