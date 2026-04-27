from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class BankerNotFoundException(DomainException):
    """Raised when a banker is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'BANKER_NOT_FOUND'

    def __init__(self, message: str = 'Banker not found') -> None:
        super().__init__(message)


class BankerNameAlreadyExistsException(DomainException):
    """Violou a UNIQUE em `bankers.name` (criar ou atualizar com nome já usado)."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'BANKER_NAME_ALREADY_EXISTS'

    def __init__(self, name: str | None = None) -> None:
        if name:
            msg = f'Já existe um banco com o nome "{name}". Escolha outro nome.'
        else:
            msg = 'Já existe um banco com este nome. Escolha outro nome.'
        super().__init__(msg)
