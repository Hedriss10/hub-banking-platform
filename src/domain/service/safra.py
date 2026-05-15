from typing import List

from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.repositories.safra import SafraRepository


class SafraService:
    def __init__(self, safra_repository: SafraRepository) -> None:
        self._safra_repository = safra_repository

    async def get_token(self) -> TokenResponse:
        return await self._safra_repository.get_token()

    async def get_bankers(self) -> List[BankerResponse]:
        return await self._safra_repository.get_bankers()

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> MargemBpoOutputDto:
        return await self._safra_repository.get_margem_bpo(margem_bpo_dto)

    async def get_financial_agreements(self) -> List[FinancialAgreementResponse]:
        return await self._safra_repository.get_financial_agreements()
