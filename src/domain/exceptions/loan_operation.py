from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class LoanOperationNotFoundException(DomainException):
    """Raised when a loan operation is missing or logically deleted."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'LOAN_OPERATION_NOT_FOUND'

    def __init__(self, message: str = 'Loan operation not found') -> None:
        super().__init__(message)
