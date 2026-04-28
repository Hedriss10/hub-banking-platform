from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationOutDTO,
    LoanOperationUpdateDTO,
)
from src.domain.repositories.loan_operation import LoanOperationRepository
from src.infrastructure.database.models.loan_operation import LoanOperation


class LoanOperationPostgresRepository(LoanOperationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_loan_operation(
        self, loan_operation: LoanOperationCreateDTO
    ) -> LoanOperationOutDTO:
        row = LoanOperation(**loan_operation.model_dump())
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return LoanOperationOutDTO.model_validate(row)

    async def get_loan_operation_by_id(self, id: UUID) -> Optional[LoanOperationOutDTO]:
        result = await self.session.execute(
            select(LoanOperation).where(
                LoanOperation.id.__eq__(id),
                LoanOperation.is_deleted.__eq__(False),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return LoanOperationOutDTO.model_validate(row)

    async def update_loan_operation(
        self,
        loan_operation_id: UUID,
        loan_operation: LoanOperationUpdateDTO,
    ) -> Optional[LoanOperationOutDTO]:
        row = await self.session.get(LoanOperation, loan_operation_id)
        if row is None or row.is_deleted:
            return None
        row.name = loan_operation.name
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return LoanOperationOutDTO.model_validate(row)

    async def delete_loan_operation(self, loan_operation_id: UUID) -> None:
        row = await self.session.get(LoanOperation, loan_operation_id)
        if row is None or row.is_deleted:
            return None
        row.is_deleted = True
        self.session.add(row)
        await self.session.commit()
        return None

    async def list_loan_operations(self) -> List[LoanOperationOutDTO]:
        result = await self.session.execute(
            select(LoanOperation)
            .where(LoanOperation.is_deleted.__eq__(False))
            .order_by(LoanOperation.name)
        )
        rows = result.scalars().all()
        return [LoanOperationOutDTO.model_validate(r) for r in rows]
