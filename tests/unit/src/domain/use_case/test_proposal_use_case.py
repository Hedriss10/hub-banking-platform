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
from src.domain.exceptions.proposal import ProposalNotFoundException
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
async def test_use_case_update_proposal_success(
    use_case: ProposalUseCase, service: AsyncMock
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
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=agg)
    service.update_proposal = AsyncMock(return_value=agg)
    assert await use_case.update_proposal(pid, dto) is agg


@pytest.mark.asyncio
async def test_use_case_update_proposal_raises_when_missing_existing(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    pid = uuid4()
    dto = ProposalUpdateDTO(name='B')
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=None)
    with pytest.raises(ProposalNotFoundException):
        await use_case.update_proposal(pid, dto)


@pytest.mark.asyncio
async def test_use_case_create_proposal_loan(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    loan = CreatedProposalLoanDTO(created_by=eid)
    service.create_proposal_loan = AsyncMock(return_value=loan)
    assert await use_case.create_proposal_loan(loan) is loan


@pytest.mark.asyncio
async def test_use_case_list_proposals(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    eid = uuid4()
    row = ProposalOutDTO(
        name='Z',
        financial_agreements_id=uuid4(),
        cpf='12345678901234',
        place_of_birth='SP',
        created_by=eid,
        id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
    )
    service.list_proposals = AsyncMock(return_value=[row])
    assert await use_case.list_proposals() == [row]


@pytest.mark.asyncio
async def test_use_case_get_proposal_aggregate_raises_when_missing(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    pid = uuid4()
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=None)
    with pytest.raises(ProposalNotFoundException):
        await use_case.get_proposal_aggregate(pid)


@pytest.mark.asyncio
async def test_use_case_get_proposal_aggregate_success(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    agg = ProposalAggregateOutDTO(
        proposal=ProposalOutDTO(
            name='OK',
            financial_agreements_id=uuid4(),
            cpf='12345678901234',
            place_of_birth='SP',
            created_by=uuid4(),
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False,
        ),
    )
    pid = agg.proposal.id
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=agg)
    assert await use_case.get_proposal_aggregate(pid) is agg


@pytest.mark.asyncio
async def test_use_case_delete_proposal_raises_when_missing(
    use_case: ProposalUseCase, service: AsyncMock
) -> None:
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=None)
    with pytest.raises(ProposalNotFoundException):
        await use_case.delete_proposal(uuid4())


@pytest.mark.asyncio
async def test_use_case_delete_proposal_success(
    use_case: ProposalUseCase, service: AsyncMock
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
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=agg)
    service.soft_delete_proposal = AsyncMock()
    await use_case.delete_proposal(pid)
    service.soft_delete_proposal.assert_awaited_once_with(pid)


@pytest.mark.asyncio
async def test_use_case_update_proposal_raises_when_update_returns_none(
    use_case: ProposalUseCase, service: AsyncMock
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
    service.get_proposal_aggregate_by_id = AsyncMock(return_value=agg)
    service.update_proposal = AsyncMock(return_value=None)
    with pytest.raises(ProposalNotFoundException):
        await use_case.update_proposal(pid, dto)
