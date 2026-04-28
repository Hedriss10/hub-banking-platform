from typing import List
from uuid import UUID

from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsOutDto,
    FinancialAgreementsUpdateDto,
)
from src.domain.use_case.financial_agreements import FinancialAgreementsUseCase
from src.interface.api.v2.schemas.financial_agreements import (
    FinancialAgreementsCreateSchema,
    FinancialAgreementsOutSchema,
    FinancialAgreementsUpdateSchema,
)


def _financial_agreement_out_to_schema(
    dto: FinancialAgreementsOutDto,
) -> FinancialAgreementsOutSchema:
    return FinancialAgreementsOutSchema(
        id=dto.id,
        name=dto.name,
        bank_id=dto.bankers_id,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        is_deleted=dto.is_deleted,
        created_by=dto.created_by,
    )


class FinancialAgreementsController:
    def __init__(self, financial_agreements_use_case: FinancialAgreementsUseCase):
        self.financial_agreements_use_case = financial_agreements_use_case

    async def list_financial_agreements(
        self, bank_id: UUID
    ) -> List[FinancialAgreementsOutSchema]:
        items = await self.financial_agreements_use_case.list_financial_agreements(
            bank_id
        )
        return [_financial_agreement_out_to_schema(row) for row in items]

    async def get_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> FinancialAgreementsOutSchema:
        dto = await self.financial_agreements_use_case.get_financial_agreement(
            financial_agreement_id
        )
        return _financial_agreement_out_to_schema(dto)

    async def create_financial_agreement(
        self,
        financial_agreement: FinancialAgreementsCreateSchema,
        created_by: UUID,
    ) -> FinancialAgreementsOutSchema:
        dto = FinancialAgreementsCreateDto(
            name=financial_agreement.name,
            bankers_id=financial_agreement.bank_id,
            created_by=created_by,
        )
        out = await self.financial_agreements_use_case.create_financial_agreement(dto)
        return _financial_agreement_out_to_schema(out)

    async def update_financial_agreement(
        self,
        financial_agreement_id: UUID,
        financial_agreement: FinancialAgreementsUpdateSchema,
    ) -> FinancialAgreementsOutSchema:
        update_dto = FinancialAgreementsUpdateDto.model_validate(
            financial_agreement.model_dump()
        )
        out = await self.financial_agreements_use_case.update_financial_agreement(
            financial_agreement_id, update_dto
        )
        return _financial_agreement_out_to_schema(out)

    async def delete_financial_agreement(self, financial_agreement_id: UUID) -> None:
        await self.financial_agreements_use_case.delete_financial_agreement(
            financial_agreement_id
        )
