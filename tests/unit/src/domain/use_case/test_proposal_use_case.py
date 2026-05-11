from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
    ProposalOutDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.service.proposal import ProposalService
from src.domain.use_case.proposal import ProposalUseCase

pytestmark = pytest.mark.unit


@pytest.fixture
def service() -> AsyncMock:
    return AsyncMock(spec=ProposalService)


@pytest.fixture
def use_case(service: AsyncMock) -> ProposalUseCase:
    return ProposalUseCase(service)


@pytest.mark.asyncio
async def test_use_case_create_proposal_with_relations(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    fa = uuid4()
    out = ProposalAggregateOutDTO(
        proposal=ProposalOutDTO(
            name='A',
            financial_agreements_id=fa,
            cpf='12345678901234',
            place_of_birth='SP',
            created_by=eid,
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False,
        ),
    )
    service.create_proposal_with_relations = AsyncMock(return_value=out)
    payload = ProposalAggregateCreateDTO(
        proposal=CreatedProposalDTO(
            name='A',
            financial_agreements_id=fa,
            cpf='12345678901234',
            place_of_birth='X',
            created_by=eid,
        ),
    )
    assert await use_case.create_proposal_with_relations(payload) is out


@pytest.mark.asyncio
async def test_use_case_create_proposal(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    fa = uuid4()
    dto = CreatedProposalDTO(
        name='A',
        financial_agreements_id=fa,
        cpf='12345678901234',
        place_of_birth='X',
        created_by=eid,
    )
    service.create_proposal = AsyncMock(return_value=dto)
    assert await use_case.create_proposal(dto) is dto


@pytest.mark.asyncio
async def test_use_case_create_proposal_account(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    acc = CreatedProposalAccountDTO(created_by=eid)
    service.create_proposal_account = AsyncMock(return_value=acc)
    assert await use_case.create_proposal_account(acc) is acc


@pytest.mark.asyncio
async def test_use_case_create_proposal_document(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    doc = CreatedProposalDocumentDTO(document_path='/p', created_by=eid)
    service.create_proposal_document = AsyncMock(return_value=doc)
    assert await use_case.create_proposal_document(doc) is doc


@pytest.mark.asyncio
async def test_use_case_create_proposal_loan(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    loan = CreatedProposalLoanDTO(created_by=eid)
    service.create_proposal_loan = AsyncMock(return_value=loan)
    assert await use_case.create_proposal_loan(loan) is loan
