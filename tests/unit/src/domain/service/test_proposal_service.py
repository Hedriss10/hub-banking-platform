from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
    ProposalOutDTO,
    ProposalUpdateDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.service.proposal import ProposalService

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repo: AsyncMock) -> ProposalService:
    return ProposalService(repo)


@pytest.mark.asyncio
async def test_create_proposal_with_relations(
    service: ProposalService, repo: AsyncMock
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
    repo.create_proposal_with_relations = AsyncMock(return_value=out)
    payload = ProposalAggregateCreateDTO(
        proposal=CreatedProposalDTO(
            name='A',
            financial_agreements_id=fa,
            cpf='12345678901234',
            place_of_birth='X',
            created_by=eid,
        ),
    )
    result = await service.create_proposal_with_relations(payload)
    assert result is out
    repo.create_proposal_with_relations.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_create_proposal(service: ProposalService, repo: AsyncMock) -> None:
    eid = uuid4()
    fa = uuid4()
    row = CreatedProposalDTO(
        name='A',
        financial_agreements_id=fa,
        cpf='12345678901234',
        place_of_birth='X',
        created_by=eid,
    )
    repo.create_proposal = AsyncMock(return_value=row)
    assert await service.create_proposal(row) is row
    repo.create_proposal.assert_awaited_once_with(row)


@pytest.mark.asyncio
async def test_create_proposal_account(
    service: ProposalService,
    repo: AsyncMock,
) -> None:
    eid = uuid4()
    acc = CreatedProposalAccountDTO(created_by=eid)
    repo.create_proposal_account = AsyncMock(return_value=acc)
    assert await service.create_proposal_account(acc) is acc


@pytest.mark.asyncio
async def test_create_proposal_document(
    service: ProposalService,
    repo: AsyncMock,
) -> None:
    eid = uuid4()
    doc = CreatedProposalDocumentDTO(document_path='/x', created_by=eid)
    repo.create_proposal_document = AsyncMock(return_value=doc)
    assert await service.create_proposal_document(doc) is doc


@pytest.mark.asyncio
async def test_create_proposal_loan(service: ProposalService, repo: AsyncMock) -> None:
    eid = uuid4()
    loan = CreatedProposalLoanDTO(created_by=eid)
    repo.create_proposal_loan = AsyncMock(return_value=loan)
    assert await service.create_proposal_loan(loan) is loan


@pytest.mark.asyncio
async def test_service_list_get_update_delete_delegate_to_repo(
    service: ProposalService, repo: AsyncMock
) -> None:
    pid = uuid4()
    agg = ProposalAggregateOutDTO(
        proposal=ProposalOutDTO(
            id=pid,
            name='A',
            financial_agreements_id=uuid4(),
            cpf='12345678901234',
            place_of_birth='SP',
            created_by=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False,
        ),
    )
    dto = ProposalUpdateDTO(name='B')

    repo.get_proposal_aggregate_by_id = AsyncMock(return_value=agg)
    assert await service.get_proposal_aggregate_by_id(pid) is agg

    repo.list_proposals = AsyncMock(return_value=[agg.proposal])
    assert await service.list_proposals() == [agg.proposal]

    repo.update_proposal = AsyncMock(return_value=agg)
    assert await service.update_proposal(pid, dto) is agg

    repo.soft_delete_proposal = AsyncMock()
    await service.soft_delete_proposal(pid)
    repo.soft_delete_proposal.assert_awaited_with(pid)
