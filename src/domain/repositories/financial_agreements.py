from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.financial_agreements import (
    FinancialAgreementsCreateDto,
    FinancialAgreementsOutDto,
    FinancialAgreementsUpdateDto,
)


class FinancialAgreementsRepository(ABC):
    @abstractmethod
    async def create_financial_agreement(
        self, financial_agreement: FinancialAgreementsCreateDto
    ) -> FinancialAgreementsOutDto: ...

    @abstractmethod
    async def get_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> Optional[FinancialAgreementsOutDto]: ...

    @abstractmethod
    async def update_financial_agreement(
        self,
        financial_agreement_id: UUID,
        financial_agreement: FinancialAgreementsUpdateDto,
    ) -> Optional[FinancialAgreementsOutDto]: ...

    @abstractmethod
    async def delete_financial_agreement(
        self, financial_agreement_id: UUID
    ) -> None: ...

    @abstractmethod
    async def list_financial_agreements(
        self, bank_id: UUID
    ) -> List[FinancialAgreementsOutDto]: ...
