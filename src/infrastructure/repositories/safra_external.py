from typing import List

from src.core.config.settings import get_settings
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
from src.infrastructure.external_apis.safra import SafraApi
from src.infrastructure.repositories.helpers.serializer_json import _json_to_banker_rows
from src.infrastructure.seed.emulator_safra import try_resolve_margin_bpo_demo_request


class SafraExternalRepository(SafraRepository):
    def __init__(self) -> None:
        self.api = SafraApi()

    async def get_token(self) -> TokenResponse:
        response = await self.api.get_token()
        return TokenResponse.model_validate(response.json())

    async def get_bankers(self) -> List[BankerResponse]:
        response = await self.api.get_bankers()
        rows = _json_to_banker_rows(response.json())
        return [BankerResponse.model_validate(row) for row in rows]

    async def get_margem_bpo(self, margem_bpo_dto: MargemBpoDto) -> MargemBpoOutputDto:
        settings = get_settings()
        emulator_on = settings.DEBUG or settings.API_SAFRA_MARGIN_RESPONSE_EMULATOR
        if emulator_on:
            demo = try_resolve_margin_bpo_demo_request(margem_bpo_dto)
            if demo is not None:
                return demo
        response = await self.api.get_margem_bpo(margem_bpo_dto)
        return MargemBpoOutputDto.model_validate(response.json())

    async def get_financial_agreements(self) -> List[FinancialAgreementResponse]:
        response = await self.api.get_financial_agreements()
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [FinancialAgreementResponse.model_validate(row) for row in rows]

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]:
        response = await self.api.post_credit_lighthouse(credit_lighthouse_dto)
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [CreditLighthouseResponse.model_validate(row) for row in rows]

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]:
        response = await self.api.list_safra_tables(convenio_id)
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [SafraTablesDto.model_validate(row) for row in rows]

    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto:
        response = await self.api.post_safra_proposal(proposal_dto)
        return ProposalResponseDto.model_validate(response.json())

    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodyDTO]:
        response = await self.api.get_employing_bodies(financial_agreement_id)
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [SafraEmployingBodyDTO.model_validate(row) for row in rows]

    async def get_professions(
        self, financial_agreement_id: int
    ) -> List[SafraProfessionsDTO]:
        response = await self.api.get_professions(financial_agreement_id)
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [SafraProfessionsDTO.model_validate(row) for row in rows]

    async def get_legal_regime(
        self, financial_agreement_id: int
    ) -> List[LegalRegimeDTO]:
        response = await self.api.get_legal_regime(financial_agreement_id)
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [LegalRegimeDTO.model_validate(row) for row in rows]

    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> List[EmployeeSituationDTO]:
        response = await self.api.get_employee_situation(
            financial_agreement_id, legal_regime_id
        )
        payload = response.json()
        rows = payload if isinstance(payload, list) else [payload]
        return [EmployeeSituationDTO.model_validate(row) for row in rows]
