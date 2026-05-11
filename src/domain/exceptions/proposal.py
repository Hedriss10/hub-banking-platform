from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ProposalNotFoundException(DomainException):
    """Raised when a proposal is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'PROPOSAL_NOT_FOUND'

    def __init__(self, message: str = 'Proposta não encontrada') -> None:
        self.message = message
        super().__init__(message)
