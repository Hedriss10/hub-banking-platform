from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class InvalidCredentialsException(DomainException):
    """Credenciais inválidas (e-mail ou senha incorretos)."""

    status_code = HTTPStatus.UNAUTHORIZED
    code = 'INVALID_CREDENTIALS'


class InvalidOrExpiredTokenException(DomainException):
    """Token ausente, inválido, malformado ou expirado."""

    status_code = HTTPStatus.UNAUTHORIZED.value
    code = 'INVALID_OR_EXPIRED_TOKEN'
