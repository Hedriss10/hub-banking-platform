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
from src.domain.dtos.safra_employing_body import SafraEmployingBodyDTO
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
from src.domain.dtos.safra_tables import SafraTablesDto
from src.domain.service.safra import SafraService


class SafraUseCase:
    def __init__(self, safra_service: SafraService) -> None:
        self._safra_service = safra_service

    async def get_token(self) -> TokenResponse:
        return await self._safra_service.get_token()

    async def get_bankers(self) -> List[BankerResponse]:
        return await self._safra_service.get_bankers()

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> MargemBpoOutputDto:
        return await self._safra_service.get_margem_bpo(margem_bpo_dto)

    async def get_financial_agreements(self) -> List[FinancialAgreementResponse]:
        return await self._safra_service.get_financial_agreements()

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]:
        return await self._safra_service.post_credit_lighthouse(credit_lighthouse_dto)

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]:
        return await self._safra_service.list_safra_tables(convenio_id)

    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto:
        return await self._safra_service.post_safra_proposal(proposal_dto)

    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodyDTO]:
        return await self._safra_service.get_employing_bodies(financial_agreement_id)
