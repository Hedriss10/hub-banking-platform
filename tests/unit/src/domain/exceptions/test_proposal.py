from http import HTTPStatus

import pytest
from src.domain.exceptions.proposal import ProposalNotFoundException

pytestmark = pytest.mark.unit


def test_proposal_not_found_exception_default() -> None:
    exc = ProposalNotFoundException()
    assert exc.status_code == HTTPStatus.NOT_FOUND.value
    assert exc.code == 'PROPOSAL_NOT_FOUND'
    assert exc.message == 'Proposta não encontrada'
