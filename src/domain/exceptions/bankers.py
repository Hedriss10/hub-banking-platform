from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class BankerNotFoundException(DomainException):
    """Raised when a banker is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'BANKER_NOT_FOUND'

    def __init__(self, message: str = 'Banker not found') -> None:
        super().__init__(message)
