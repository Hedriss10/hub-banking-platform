from http import HTTPStatus


class DomainException(Exception):
    """
    Classe para exceções específicas de domínio na aplicação.
    """

    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'DOMAIN_ERROR'


class MultipleException(Exception):
    """
    Classe para representar múltiplas exceções ocorridas simultaneamente.
    """

    status_code: int = HTTPStatus.BAD_REQUEST
    code: str = 'MULTIPLE_ERRORS'


class RequestValidationErrorException(Exception):
    """Raised when request validation fails."""

    status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY.value
    code: str = 'VALIDATION_ERROR'


class InfrastructureException(Exception):
    """Raised when infrastructure operation fails."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    code: str = 'INTERNAL_ERROR'


class DatabaseException(InfrastructureException):
    """Raised when database operation fails."""

    code: str = 'DATABASE_ERROR'
    message: str


class DuplicatedException(InfrastructureException):
    """Raised when database operation fails."""

    status_code: int = HTTPStatus.CONFLICT.value
    code: str = 'DUPLICATED_ERROR'


class NotFoundException(InfrastructureException):
    """Raised when database operation fails."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'NOT_FOUND_ERROR'
