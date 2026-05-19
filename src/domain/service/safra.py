from typing import List

from src.domain.dtos.employee_situation import EmployeeSituationDTO
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
from src.domain.dtos.safra_legal_regime import LegalRegimeDTO
from src.domain.dtos.safra_professions import SafraProfessionsDTO
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
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

    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto:
        return await self._safra_repository.post_safra_proposal(proposal_dto)

    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodyDTO]:
        return await self._safra_repository.get_employing_bodies(financial_agreement_id)

    async def get_professions(
        self, financial_agreement_id: int
    ) -> List[SafraProfessionsDTO]:
        return await self._safra_repository.get_professions(financial_agreement_id)

    async def get_legal_regime(
        self, financial_agreement_id: int
    ) -> List[LegalRegimeDTO]:
        return await self._safra_repository.get_legal_regime(financial_agreement_id)

    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> List[EmployeeSituationDTO]:
        return await self._safra_repository.get_employee_situation(
            financial_agreement_id, legal_regime_id
        )
