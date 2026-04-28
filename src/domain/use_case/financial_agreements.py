from typing import List
from uuid import UUID

from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsOutDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.exceptions.financial_agreements import (
    FinancialAgreementNotFoundException,
)
from src.domain.service.financial_agreements import FinancialAgreementsService


class FinancialAgreementsUseCase:
    def __init__(self, financial_agreements_service: FinancialAgreementsService):
        self.financial_agreements_service = financial_agreements_service

    async def create_financial_agreement(
        self, financial_agreement: FinancialAgreementsCreateDto
    ) -> FinancialAgreementsOutDto:
        return await self.financial_agreements_service.create_financial_agreement(
            financial_agreement
        )

    async def get_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> FinancialAgreementsOutDto:
        agreement = await self.financial_agreements_service.get_financial_agreement(
            financial_agreement_id
        )
        if not agreement:
            raise FinancialAgreementNotFoundException(
                message=(
                    f'Financial agreement with id {financial_agreement_id} not found'
                ),
            )
        return agreement

    async def update_financial_agreement(
        self,
        financial_agreement_id: UUID,
        data: FinancialAgreementsUpdateDto,
    ) -> FinancialAgreementsOutDto:
        existing = await self.financial_agreements_service.get_financial_agreement(
            financial_agreement_id
        )
        if not existing:
            raise FinancialAgreementNotFoundException(
                message=(
                    f'Financial agreement with id {financial_agreement_id} not found'
                ),
            )
        updated = await self.financial_agreements_service.update_financial_agreement(
            financial_agreement_id, data
        )
        if not updated:
            raise FinancialAgreementNotFoundException(
                message=(
                    f'Financial agreement with id {financial_agreement_id} not found'
                ),
            )
        return updated

    async def delete_financial_agreement(self, financial_agreement_id: UUID) -> None:
        existing = await self.financial_agreements_service.get_financial_agreement(
            financial_agreement_id
        )
        if not existing:
            raise FinancialAgreementNotFoundException(
                message=(
                    f'Financial agreement with id {financial_agreement_id} not found'
                ),
            )
        return await self.financial_agreements_service.delete_financial_agreement(
            financial_agreement_id
        )

    async def list_financial_agreements(
        self, bank_id: UUID
    ) -> List[FinancialAgreementsOutDto]:
        return await self.financial_agreements_service.list_financial_agreements(
            bank_id
        )
