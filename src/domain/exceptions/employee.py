from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class EmployeeNotFoundException(DomainException):
    """Raised when an employee is missing or logically deleted."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'EMPLOYEE_NOT_FOUND'

    def __init__(self, message: str = 'Employee not found') -> None:
        super().__init__(message)


class EmployeeAlreadyExistsException(DomainException):
    """Raised when email or document violates a uniqueness constraint."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'EMPLOYEE_ALREADY_EXISTS'

    def __init__(
        self,
        message: str = 'An employee with this email or document already exists.',
    ) -> None:
        super().__init__(message)
