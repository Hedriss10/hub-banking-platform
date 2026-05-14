from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class SafraBatchSearchNotFoundException(DomainException):
    """Nenhuma linha persistida para o batch_job_id solicitado."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'SAFRA_BATCH_SEARCH_NOT_FOUND'

    def __init__(
        self,
        message: str = 'Resultados do lote não encontrados no armazenamento',
    ) -> None:
        self.message = message
        super().__init__(message)
