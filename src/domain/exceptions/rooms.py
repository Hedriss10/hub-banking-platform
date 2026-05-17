from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class RoomNotFoundException(DomainException):
    """Raised when the room is missing or has been logically deleted."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'ROOM_NOT_FOUND'

    def __init__(self, message: str = 'Room not found') -> None:
        super().__init__(message)


class RoomAlreadyExistsException(DomainException):
    """Raised when the room already exists."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'ROOM_ALREADY_EXISTS'

    def __init__(self, message: str = 'Room already exists') -> None:
        super().__init__(message)
