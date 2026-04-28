from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsOutDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.repositories.financial_agreements import FinancialAgreementsRepository
from src.infrastructure.database.models.financial_agreements import (
    FinancialAgreementsModel,
)


class FinancialAgreementsPostgresRepository(FinancialAgreementsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_financial_agreement(
        self, financial_agreement: FinancialAgreementsCreateDto
    ) -> FinancialAgreementsOutDto:
        row = FinancialAgreementsModel(**financial_agreement.model_dump())
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return FinancialAgreementsOutDto.model_validate(row)

    async def get_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> Optional[FinancialAgreementsOutDto]:
        result = await self.session.execute(
            select(FinancialAgreementsModel).where(
                FinancialAgreementsModel.id.__eq__(financial_agreement_id),
                FinancialAgreementsModel.is_deleted.__eq__(False),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return FinancialAgreementsOutDto.model_validate(row)

    async def update_financial_agreement(
        self,
        financial_agreement_id: UUID,
        data: FinancialAgreementsUpdateDto,
    ) -> Optional[FinancialAgreementsOutDto]:
        row = await self.session.get(FinancialAgreementsModel, financial_agreement_id)
        if row is None or row.is_deleted:
            return None
        row.name = data.name
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return FinancialAgreementsOutDto.model_validate(row)

    async def delete_financial_agreement(self, financial_agreement_id: UUID) -> None:
        row = await self.session.get(FinancialAgreementsModel, financial_agreement_id)
        if row is None or row.is_deleted:
            return None
        row.is_deleted = True
        self.session.add(row)
        await self.session.commit()
        return None

    async def list_financial_agreements(
        self, bank_id: UUID
    ) -> List[FinancialAgreementsOutDto]:
        result = await self.session.execute(
            select(FinancialAgreementsModel)
            .where(
                FinancialAgreementsModel.is_deleted.__eq__(False),
                FinancialAgreementsModel.bankers_id.__eq__(bank_id),
            )
            .order_by(FinancialAgreementsModel.name)
        )
        rows = result.scalars().all()
        return [
            FinancialAgreementsOutDto.model_validate(financial_agreement)
            for financial_agreement in rows
        ]
