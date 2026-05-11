from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.proposal import (
    CreatedProposalDTO,
    ProposalAggregateCreateDTO,
    ProposalAggregateOutDTO,
    ProposalOutDTO,
    ProposalUpdateDTO,
)
from src.domain.dtos.proposal_account import (
    CreatedProposalAccountDTO,
    ProposalAccountOutDTO,
)
from src.domain.dtos.proposal_document import (
    CreatedProposalDocumentDTO,
    ProposalDocumentOutDTO,
)
from src.domain.dtos.proposal_loan import (
    CreatedProposalLoanDTO,
    ProposalLoanOutDTO,
)
from src.domain.repositories.proposal import IProposalRepository
from src.infrastructure.database.models.common.document import DocumentType
from src.infrastructure.database.models.common.gender import Gender
from src.infrastructure.database.models.common.proposal_loan import ProposalLoanStatus
from src.infrastructure.database.models.proposal import ProposalModel
from src.infrastructure.database.models.proposal_account import (
    ProposalPaymentAccountModel,
)
from src.infrastructure.database.models.proposal_document import ProposalDocumentModel
from src.infrastructure.database.models.proposal_loan import ProposalLoanModel


def _row_to_dto[T](row: object, dto_class: type[T]) -> T:
    data = {
        column.name: getattr(row, column.name)
        for column in row.__table__.columns  # type: ignore[attr-defined]
    }
    for key, value in data.items():
        if isinstance(value, Enum):
            data[key] = value.value
    return dto_class.model_validate(data)  # type: ignore[attr-defined]


def _enum_value(value: object, enum_class: type[Enum]) -> Enum | None:
    if value is None:
        return None
    if isinstance(value, enum_class):
        return value
    if isinstance(value, Enum):
        return enum_class(value.value)
    return enum_class(value)


def _proposal_update_values(payload: ProposalUpdateDTO) -> dict[str, object]:
    raw = payload.model_dump(exclude_unset=True, exclude_none=True)
    if 'document' in raw:
        raw['document'] = _enum_value(raw['document'], DocumentType)
    if 'gender' in raw:
        raw['gender'] = _enum_value(raw['gender'], Gender)
    return raw


class ProposalPostgresRepository(IProposalRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _proposal_children_aggregate(
        self, proposal_row: ProposalModel
    ) -> ProposalAggregateOutDTO:
        pid = proposal_row.id

        acc_stmt = (
            select(ProposalPaymentAccountModel)
            .where(ProposalPaymentAccountModel.proposal_id.__eq__(pid))
            .where(ProposalPaymentAccountModel.is_deleted.is_(False))
            .limit(1)
        )
        acc_result = await self.session.execute(acc_stmt)
        account_row = acc_result.scalar_one_or_none()

        doc_stmt = (
            select(ProposalDocumentModel)
            .where(ProposalDocumentModel.proposal_id.__eq__(pid))
            .where(ProposalDocumentModel.is_deleted.is_(False))
        )
        doc_rows = (await self.session.execute(doc_stmt)).scalars().all()

        loan_stmt = (
            select(ProposalLoanModel)
            .where(ProposalLoanModel.proposal_id.__eq__(pid))
            .where(ProposalLoanModel.is_deleted.is_(False))
        )
        loan_rows = (await self.session.execute(loan_stmt)).scalars().all()

        return ProposalAggregateOutDTO(
            proposal=_row_to_dto(proposal_row, ProposalOutDTO),
            account=(
                _row_to_dto(account_row, ProposalAccountOutDTO)
                if account_row is not None
                else None
            ),
            documents=[_row_to_dto(dr, ProposalDocumentOutDTO) for dr in doc_rows],
            loans=[_row_to_dto(lr, ProposalLoanOutDTO) for lr in loan_rows],
        )

    async def get_proposal_aggregate_by_id(
        self, proposal_id: UUID
    ) -> Optional[ProposalAggregateOutDTO]:
        try:
            proposal_stmt = (
                select(ProposalModel)
                .where(ProposalModel.id.__eq__(proposal_id))
                .where(ProposalModel.is_deleted.is_(False))
            )
            proposal_result = await self.session.execute(proposal_stmt)
            proposal_row = proposal_result.scalar_one_or_none()
            if proposal_row is None:
                return None
            return await self._proposal_children_aggregate(proposal_row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def list_proposals(self) -> list[ProposalOutDTO]:
        try:
            stmt = (
                select(ProposalModel)
                .where(ProposalModel.is_deleted.is_(False))
                .order_by(ProposalModel.updated_at.desc())
            )
            rows = list((await self.session.execute(stmt)).scalars())
            return [_row_to_dto(row, ProposalOutDTO) for row in rows]
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_proposal(
        self, proposal_id: UUID, payload: ProposalUpdateDTO
    ) -> Optional[ProposalAggregateOutDTO]:
        try:
            values = _proposal_update_values(payload)
            if not values:
                return await self.get_proposal_aggregate_by_id(proposal_id)

            stmt = (
                update(ProposalModel)
                .where(ProposalModel.id.__eq__(proposal_id))
                .where(ProposalModel.is_deleted.is_(False))
                .values(**values)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return await self.get_proposal_aggregate_by_id(proposal_id)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def soft_delete_proposal(self, proposal_id: UUID) -> None:
        try:
            stmt = (
                update(ProposalModel)
                .where(ProposalModel.id.__eq__(proposal_id))
                .where(ProposalModel.is_deleted.is_(False))
                .values(is_deleted=True)
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def create_proposal_with_relations(
        self, payload: ProposalAggregateCreateDTO
    ) -> ProposalAggregateOutDTO:
        try:
            proposal_data = payload.proposal.model_dump()
            proposal_data['document'] = _enum_value(
                proposal_data.get('document'), DocumentType
            )
            proposal_data['gender'] = _enum_value(proposal_data.get('gender'), Gender)

            proposal_row = ProposalModel(**proposal_data)
            self.session.add(proposal_row)
            await self.session.flush()

            account_row = None
            if payload.account:
                account_row = ProposalPaymentAccountModel(
                    **payload.account.model_dump(exclude={'proposal_id'}),
                    proposal_id=proposal_row.id,
                )
                self.session.add(account_row)

            document_rows = [
                ProposalDocumentModel(
                    **document.model_dump(exclude={'proposal_id'}),
                    proposal_id=proposal_row.id,
                )
                for document in payload.documents
            ]
            self.session.add_all(document_rows)

            loan_rows = []
            for loan in payload.loans:
                loan_data = loan.model_dump(exclude={'proposal_id'})
                loan_data['status'] = _enum_value(
                    loan_data.get('status'), ProposalLoanStatus
                )
                loan_rows.append(
                    ProposalLoanModel(**loan_data, proposal_id=proposal_row.id)
                )
            self.session.add_all(loan_rows)

            await self.session.flush()
            await self.session.refresh(proposal_row)
            if account_row is not None:
                await self.session.refresh(account_row)
            for row in [*document_rows, *loan_rows]:
                await self.session.refresh(row)
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

        return ProposalAggregateOutDTO(
            proposal=_row_to_dto(proposal_row, ProposalOutDTO),
            account=(
                _row_to_dto(account_row, ProposalAccountOutDTO)
                if account_row is not None
                else None
            ),
            documents=[
                _row_to_dto(document_row, ProposalDocumentOutDTO)
                for document_row in document_rows
            ],
            loans=[_row_to_dto(loan_row, ProposalLoanOutDTO) for loan_row in loan_rows],
        )

    async def create_proposal(self, proposal: CreatedProposalDTO) -> CreatedProposalDTO:
        try:
            data = proposal.model_dump()
            data['document'] = _enum_value(data.get('document'), DocumentType)
            data['gender'] = _enum_value(data.get('gender'), Gender)
            row = ProposalModel(**data)
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
        return _row_to_dto(row, CreatedProposalDTO)

    async def create_proposal_account(
        self, proposal_account: CreatedProposalAccountDTO
    ) -> CreatedProposalAccountDTO:
        try:
            row = ProposalPaymentAccountModel(**proposal_account.model_dump())
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
        return _row_to_dto(row, CreatedProposalAccountDTO)

    async def create_proposal_document(
        self, proposal_document: CreatedProposalDocumentDTO
    ) -> CreatedProposalDocumentDTO:
        try:
            row = ProposalDocumentModel(**proposal_document.model_dump())
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
        return _row_to_dto(row, CreatedProposalDocumentDTO)

    async def create_proposal_loan(
        self, proposal_loan: CreatedProposalLoanDTO
    ) -> CreatedProposalLoanDTO:
        try:
            data = proposal_loan.model_dump()
            data['status'] = _enum_value(data.get('status'), ProposalLoanStatus)
            row = ProposalLoanModel(**data)
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
        return _row_to_dto(row, CreatedProposalLoanDTO)
