from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class EmployeeNotFoundException(DomainException):
    """
    Exception raised when an employee is not found.
    """

    status_code = HTTPStatus.NOT_FOUND
    code = 'EMPLOYEE_NOT_FOUND'


class EmployeeAlreadyExistsException(DomainException):
    """
    Exception raised when an employee already exists.
    """

    status_code = HTTPStatus.CONFLICT
    code = 'EMPLOYEE_ALREADY_EXISTS'
