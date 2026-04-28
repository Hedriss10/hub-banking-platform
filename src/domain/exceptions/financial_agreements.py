from http import HTTPStatus

from src.core.exceptions.custom import DomainException


class FinancialAgreementsDomainException(DomainException):
    """Domain-level financial agreement errors."""

    status_code: int = HTTPStatus.BAD_REQUEST.value
    code: str = 'FINANCIAL_AGREEMENTS_DOMAIN_ERROR'


class FinancialAgreementNotFoundException(DomainException):
    """Raised when a financial agreement is missing or logically deleted."""

    status_code: int = HTTPStatus.NOT_FOUND.value
    code: str = 'FINANCIAL_AGREEMENT_NOT_FOUND'

    def __init__(self, message: str = 'Financial agreement not found') -> None:
        super().__init__(message)
