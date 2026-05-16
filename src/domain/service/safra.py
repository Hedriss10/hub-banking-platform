from typing import List

from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_tables import SafraTablesDto
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

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]:
        return await self._safra_repository.post_credit_lighthouse(
            credit_lighthouse_dto
        )

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]:
        return await self._safra_repository.list_safra_tables(convenio_id)
