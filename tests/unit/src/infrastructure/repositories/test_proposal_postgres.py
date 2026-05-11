from datetime import datetime, timezone
from enum import Enum
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
)
from src.domain.dtos.proposal_account import CreatedProposalAccountDTO
from src.domain.dtos.proposal_document import CreatedProposalDocumentDTO
from src.domain.dtos.proposal_loan import CreatedProposalLoanDTO
from src.domain.enum.document import DocumentType as DomainDocumentType
from src.domain.enum.gender import Gender
from src.domain.enum.proposal_loan import ProposalLoanStatus
from src.infrastructure.database.models.common.document import DocumentType
from src.infrastructure.database.models.common.gender import Gender as SaGender
from src.infrastructure.repositories.proposal_postgres import (
    ProposalPostgresRepository,
    _enum_value,
    _row_to_dto,
)

pytestmark = pytest.mark.unit


class _Col:
    __slots__ = ('name',)

    def __init__(self, name: str) -> None:
        self.name = name


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def repository(mock_session: AsyncMock) -> ProposalPostgresRepository:
    return ProposalPostgresRepository(mock_session)


def test_enum_value_none() -> None:
    assert _enum_value(None, DocumentType) is None


def test_enum_value_already_member() -> None:
    assert _enum_value(DocumentType.CPF, DocumentType) == DocumentType.CPF


def test_enum_value_from_string() -> None:
    assert _enum_value('RG', DocumentType) == DocumentType.RG


def test_enum_value_other_enum_coerced() -> None:
    class Other(Enum):
        X = 'MALE'

    out = _enum_value(Other.X, SaGender)
    assert out == SaGender.MALE


def test_row_to_dto_converts_enum_to_value() -> None:
    eid = uuid4()
    fid = uuid4()
    cols = (
        'name',
        'cpf',
        'financial_agreements_id',
        'place_of_birth',
        'created_by',
        'document',
    )
    mock_table = MagicMock()
    mock_table.columns = [_Col(n) for n in cols]
    mock_row = MagicMock()
    mock_row.__table__ = mock_table
    mock_row.name = 'Ana'
    mock_row.cpf = '12345678901234'
    mock_row.financial_agreements_id = fid
    mock_row.place_of_birth = 'SP'
    mock_row.created_by = eid
    mock_row.document = DocumentType.CNH

    dto = _row_to_dto(mock_row, CreatedProposalDTO)
    assert dto.document == DomainDocumentType.CNH


@pytest.mark.asyncio
async def test_create_proposal_with_relations_success(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    fid = uuid4()

    stash: list = []

    def add_side_effect(obj: object) -> None:
        stash.append(obj)

    async def flush_side_effect() -> None:
        for o in stash:
            if getattr(o, 'id', None) is None:
                object.__setattr__(o, 'id', uuid4())

    async def refresh_side_effect(obj: object) -> None:
        now = datetime.now(timezone.utc)
        if getattr(obj, 'created_at', None) is None:
            object.__setattr__(obj, 'created_at', now)
        if getattr(obj, 'updated_at', None) is None:
            object.__setattr__(obj, 'updated_at', now)
        if hasattr(obj, 'is_deleted') and getattr(obj, 'is_deleted', None) is None:
            object.__setattr__(obj, 'is_deleted', False)

    mock_session.add = MagicMock(side_effect=add_side_effect)

    def extend_stash(rows: object) -> None:
        stash.extend(rows)  # type: ignore[arg-type]

    mock_session.add_all = MagicMock(side_effect=extend_stash)

    mock_session.flush = AsyncMock(side_effect=flush_side_effect)
    mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
    mock_session.commit = AsyncMock()

    payload = ProposalAggregateCreateDTO(
        proposal=CreatedProposalDTO(
            name='N',
            financial_agreements_id=fid,
            cpf='12345678901234',
            document=DomainDocumentType.CPF,
            gender=Gender.MALE,
            place_of_birth='SP',
            created_by=eid,
        ),
        account=CreatedProposalAccountDTO(
            bank_agency='1',
            created_by=eid,
        ),
        documents=[
            CreatedProposalDocumentDTO(document_path='/a.pdf', created_by=eid),
        ],
        loans=[
            CreatedProposalLoanDTO(
                status=ProposalLoanStatus.WAITING_TYPING,
                created_by=eid,
                finance_table_id=1,
                loan_operation_id=2,
            ),
        ],
    )

    out = await repository.create_proposal_with_relations(payload)
    assert out.proposal.name == 'N'
    assert out.account is not None
    assert len(out.documents) == 1
    assert len(out.loans) == 1
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_proposal_with_relations_rollback(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    fid = uuid4()
    mock_session.add = MagicMock()
    mock_session.add_all = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('db'))

    payload = ProposalAggregateCreateDTO(
        proposal=CreatedProposalDTO(
            name='N',
            financial_agreements_id=fid,
            cpf='12345678901234',
            place_of_birth='SP',
            created_by=eid,
        ),
    )

    with pytest.raises(DatabaseException):
        await repository.create_proposal_with_relations(payload)
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_proposal_success(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    fid = uuid4()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    async def refresh_ok(obj: object) -> None:
        now = datetime.now(timezone.utc)
        object.__setattr__(obj, 'created_at', now)
        object.__setattr__(obj, 'updated_at', now)
        object.__setattr__(obj, 'is_deleted', False)

    mock_session.refresh = AsyncMock(side_effect=refresh_ok)

    async def flush_side_effect() -> None:
        call = mock_session.add.call_args_list[0][0][0]
        if getattr(call, 'id', None) is None:
            object.__setattr__(call, 'id', uuid4())

    mock_session.flush = AsyncMock(side_effect=flush_side_effect)

    dto = CreatedProposalDTO(
        name='Z',
        financial_agreements_id=fid,
        cpf='99999999991234',
        place_of_birth='RJ',
        gender=Gender.FEMALE,
        document=DomainDocumentType.RG,
        created_by=eid,
    )
    out = await repository.create_proposal(dto)
    assert out.name == 'Z'
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_proposal_rollback(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    fid = uuid4()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('fail'))
    dto = CreatedProposalDTO(
        name='Z',
        financial_agreements_id=fid,
        cpf='88888888881234',
        place_of_birth='RJ',
        created_by=eid,
    )
    with pytest.raises(DatabaseException):
        await repository.create_proposal(dto)
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_proposal_account_success_and_rollback(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    entity = CreatedProposalAccountDTO(created_by=eid)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    async def refresh_row(obj: object) -> None:
        now = datetime.now(timezone.utc)
        object.__setattr__(obj, 'id', uuid4())
        object.__setattr__(obj, 'created_at', now)
        object.__setattr__(obj, 'updated_at', now)
        object.__setattr__(obj, 'is_deleted', False)

    mock_session.refresh = AsyncMock(side_effect=refresh_row)
    await repository.create_proposal_account(entity)
    mock_session.commit.assert_awaited_once()

    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('x'))
    with pytest.raises(DatabaseException):
        await repository.create_proposal_account(entity)
    mock_session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_create_proposal_document_success_and_rollback(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    pid = uuid4()
    entity = CreatedProposalDocumentDTO(
        document_path='/d', created_by=eid, proposal_id=pid
    )
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    async def refresh_row(obj: object) -> None:
        now = datetime.now(timezone.utc)
        object.__setattr__(obj, 'id', uuid4())
        object.__setattr__(obj, 'created_at', now)
        object.__setattr__(obj, 'updated_at', now)
        object.__setattr__(obj, 'is_deleted', False)

    mock_session.refresh = AsyncMock(side_effect=refresh_row)
    await repository.create_proposal_document(entity)
    mock_session.commit.assert_awaited_once()

    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('x'))
    with pytest.raises(DatabaseException):
        await repository.create_proposal_document(entity)


@pytest.mark.asyncio
async def test_create_proposal_loan_success_and_rollback(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    entity = CreatedProposalLoanDTO(
        status=ProposalLoanStatus.PAID,
        created_by=eid,
    )
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    async def refresh_row(obj: object) -> None:
        now = datetime.now(timezone.utc)
        object.__setattr__(obj, 'id', uuid4())
        object.__setattr__(obj, 'created_at', now)
        object.__setattr__(obj, 'updated_at', now)
        object.__setattr__(obj, 'is_deleted', False)

    mock_session.refresh = AsyncMock(side_effect=refresh_row)
    await repository.create_proposal_loan(entity)
    mock_session.commit.assert_awaited_once()

    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError('x'))
    with pytest.raises(DatabaseException):
        await repository.create_proposal_loan(entity)


@pytest.mark.asyncio
async def test_create_proposal_without_account_or_children(
    repository: ProposalPostgresRepository,
    mock_session: AsyncMock,
) -> None:
    eid = uuid4()
    fid = uuid4()

    stash: list = []

    def capture_add(o: object) -> None:
        stash.append(o)

    def extend_stash(rows: object) -> None:
        stash.extend(rows)  # type: ignore[arg-type]

    mock_session.add = MagicMock(side_effect=capture_add)
    mock_session.add_all = MagicMock(side_effect=extend_stash)

    async def flush_side_effect() -> None:
        for o in stash:
            if getattr(o, 'id', None) is None:
                object.__setattr__(o, 'id', uuid4())

    async def refresh_side_effect(obj: object) -> None:
        now = datetime.now(timezone.utc)
        object.__setattr__(obj, 'created_at', now)
        object.__setattr__(obj, 'updated_at', now)
        if hasattr(obj, 'is_deleted') and getattr(obj, 'is_deleted', None) is None:
            object.__setattr__(obj, 'is_deleted', False)

    mock_session.flush = AsyncMock(side_effect=flush_side_effect)
    mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)
    mock_session.commit = AsyncMock()

    payload = ProposalAggregateCreateDTO(
        proposal=CreatedProposalDTO(
            name='Only',
            financial_agreements_id=fid,
            cpf='11111111111234',
            place_of_birth='X',
            created_by=eid,
        ),
    )
    out = await repository.create_proposal_with_relations(payload)
    assert out.account is None
    assert out.documents == []
    assert out.loans == []
