from typing import List, Optional
from uuid import UUID

from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsOutDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.repositories.financial_agreements import FinancialAgreementsRepository


class FinancialAgreementsService:
    def __init__(self, financial_agreements_repository: FinancialAgreementsRepository):
        self.financial_agreements_repository = financial_agreements_repository

    async def create_financial_agreement(
        self, financial_agreement: FinancialAgreementsCreateDto
    ) -> FinancialAgreementsOutDto:
        return await self.financial_agreements_repository.create_financial_agreement(
            financial_agreement
        )

    async def get_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> Optional[FinancialAgreementsOutDto]:
        return await self.financial_agreements_repository.get_financial_agreement(
            financial_agreement_id
        )

    async def update_financial_agreement(
        self,
        financial_agreement_id: UUID,
        financial_agreement: FinancialAgreementsUpdateDto,
    ) -> Optional[FinancialAgreementsOutDto]:
        return await self.financial_agreements_repository.update_financial_agreement(
            financial_agreement_id, financial_agreement
        )

    async def delete_financial_agreement(self, financial_agreement_id: UUID) -> None:
        return await self.financial_agreements_repository.delete_financial_agreement(
            financial_agreement_id
        )

    async def list_financial_agreements(
        self, bank_id: UUID
    ) -> List[FinancialAgreementsOutDto]:
        return await self.financial_agreements_repository.list_financial_agreements(
            bank_id
        )
