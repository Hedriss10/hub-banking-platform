from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class ProposalNotFoundException(DomainException):
    """Raised when a proposal is not found."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'PROPOSAL_NOT_FOUND'
    message: str = 'Proposta não encontrada'
