"""Tests for financial-agreements domain exceptions."""

import pytest
from src.domain.exceptions.financial_agreements import (
    FinancialAgreementNotFoundException,
    FinancialAgreementsDomainException,
)

pytestmark = pytest.mark.unit


def test_financial_agreements_domain_exception_metadata() -> None:
    exc = FinancialAgreementsDomainException('bad')
    assert exc.code == 'FINANCIAL_AGREEMENTS_DOMAIN_ERROR'


def test_financial_agreement_not_found_default_message() -> None:
    exc = FinancialAgreementNotFoundException()
    assert str(exc) == 'Financial agreement not found'
    assert exc.code == 'FINANCIAL_AGREEMENT_NOT_FOUND'


def test_financial_agreement_not_found_custom_message() -> None:
    exc = FinancialAgreementNotFoundException(message='Custom')
    assert str(exc) == 'Custom'
