from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.proposal import ProposalAggregateOutDTO, ProposalOutDTO
from src.domain.use_case.proposal import ProposalUseCase
from src.interface.api.v2.controller.proposal import ProposalController
from src.interface.api.v2.schemas.proposal import (
    ProposalAccountSchema,
    ProposalCreateSchema,
    ProposalDocumentSchema,
    ProposalLoanSchema,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def use_case() -> AsyncMock:
    return AsyncMock(spec=ProposalUseCase)


@pytest.fixture
def controller(use_case: AsyncMock) -> ProposalController:
    return ProposalController(use_case)


def _minimal_out(eid):
    fid = uuid4()
    pid = uuid4()
    now = datetime.now(timezone.utc)
    return ProposalAggregateOutDTO(
        proposal=ProposalOutDTO(
            name='Cliente',
            financial_agreements_id=fid,
            cpf='12345678901234',
            place_of_birth='Brasil',
            created_by=eid,
            id=pid,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        ),
        account=None,
        documents=[],
        loans=[],
    )


@pytest.mark.asyncio
async def test_controller_create_proposal_minimal(
    controller: ProposalController, use_case: AsyncMock
) -> None:
    eid = uuid4()
    out = _minimal_out(eid)
    use_case.create_proposal_with_relations = AsyncMock(return_value=out)

    payload = ProposalCreateSchema(
        proposal={
            'name': 'Cliente',
            'financial_agreements_id': out.proposal.financial_agreements_id,
            'cpf': '12345678901234',
            'place_of_birth': 'Brasil',
        },
    )
    resp = await controller.create_proposal(payload, eid)
    assert resp.proposal.id == out.proposal.id
    assert resp.documents == []
    use_case.create_proposal_with_relations.assert_awaited_once()


@pytest.mark.asyncio
async def test_controller_create_proposal_with_nested(
    controller: ProposalController, use_case: AsyncMock
) -> None:
    eid = uuid4()
    out = _minimal_out(eid)
    use_case.create_proposal_with_relations = AsyncMock(return_value=out)

    bid = uuid4()
    payload = ProposalCreateSchema(
        proposal={
            'name': 'Cliente',
            'financial_agreements_id': out.proposal.financial_agreements_id,
            'cpf': '12345678901234',
            'place_of_birth': 'Brasil',
        },
        account=ProposalAccountSchema(bank_agency='1', bank_id=bid),
        documents=[ProposalDocumentSchema(document_path='https://x/a.pdf')],
        loans=[ProposalLoanSchema(term_start=12, term_end=24)],
    )
    await controller.create_proposal(payload, eid)
    call_arg = use_case.create_proposal_with_relations.await_args.args[0]
    assert call_arg.account is not None
    assert call_arg.account.bank_agency == '1'
    assert len(call_arg.documents) == 1
    assert len(call_arg.loans) == 1
