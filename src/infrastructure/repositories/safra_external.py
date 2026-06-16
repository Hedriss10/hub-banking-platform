from typing import List, TypeVar

from pydantic import BaseModel

from src.core.config.settings import get_settings
from src.domain.dtos.employee_situation import EmployeeSituationDTO
from src.domain.dtos.safra import (
    BankerResponse,
    MargemBpoDto,
    MargemBpoOutputDto,
    TokenResponse,
)
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    CalculationPortRefinResponseDto,
    CalculationRefinRequestDto,
    CalculationRequestDto,
    CalculationResponseDto,
)
from src.domain.dtos.safra_catalog import (
    SafraAgencyDto,
    SafraEmploymentBondDto,
    SafraInterestTableBandDto,
    SafraOperationalGuideDto,
    SafraPositionDto,
)
from src.domain.dtos.safra_contracts import (
    ContractFinancialDto,
    ContractLoanDto,
    ContractRegistrationDataDto,
    ContractStatusDto,
)
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_employing_body import SafraEmployingBodyDTO
from src.domain.dtos.safra_financial_agreements import FinancialAgreementResponse
from src.domain.dtos.safra_formalization_link import (
    FormalizationLinkQueryDto,
    FormalizationLinkResponseDto,
)
from src.domain.dtos.safra_leads import LeadDto, LeadReturnUploadItemDto
from src.domain.dtos.safra_legal_regime import LegalRegimeDTO
from src.domain.dtos.safra_professions import SafraProfessionsDTO
from src.domain.dtos.safra_proposal import ProposalDto, ProposalResponseDto
from src.domain.dtos.safra_proposal_attachment import ProposalAttachmentDto
from src.domain.dtos.safra_proposal_tracking import (
    FormalizationTrackingDto,
    ParadinhaResponseDto,
    ProposalFlowStepDto,
    ProposalListItemDto,
    ProposalListQueryDto,
)
from src.domain.dtos.safra_tables import SafraTablesDto
from src.domain.repositories.safra import SafraRepository
from src.infrastructure.external_apis.safra import SafraApi
from src.infrastructure.repositories.helpers.safra_json import rows_from_json
from src.infrastructure.repositories.helpers.serializer_json import _json_to_banker_rows
from src.infrastructure.seed.emulator_safra import try_resolve_margin_bpo_demo_request

T = TypeVar('T', bound=BaseModel)


def _map_rows(payload: object, model: type[T]) -> List[T]:
    return [model.model_validate(row) for row in rows_from_json(payload)]


class SafraExternalRepository(SafraRepository):
    def __init__(self) -> None:
        self.api = SafraApi()

    async def _list_from_api(
        self,
        fetch,
        model: type[T],
    ) -> List[T]:
        response = await fetch()
        return _map_rows(response.json(), model)

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
        return await self._list_from_api(
            self.api.get_financial_agreements,
            FinancialAgreementResponse,
        )

    async def get_operational_guide(self, convenio_id: int) -> SafraOperationalGuideDto:
        response = await self.api.get_operational_guide(convenio_id)
        return SafraOperationalGuideDto.model_validate(response.json())

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]:
        response = await self.api.post_credit_lighthouse(credit_lighthouse_dto)
        return _map_rows(response.json(), CreditLighthouseResponse)

    async def post_calculo_novo(
        self, calculation_dto: CalculationRequestDto
    ) -> CalculationResponseDto:
        response = await self.api.post_calculo_novo(calculation_dto)
        return CalculationResponseDto.model_validate(response.json())

    async def post_calculo_refin(
        self, calculation_dto: CalculationRefinRequestDto
    ) -> CalculationResponseDto:
        response = await self.api.post_calculo_refin(calculation_dto)
        return CalculationResponseDto.model_validate(response.json())

    async def post_calculo_portabilidade(
        self, calculation_dto: CalculationPortabilityRequestDto
    ) -> CalculationResponseDto:
        response = await self.api.post_calculo_portabilidade(calculation_dto)
        return CalculationResponseDto.model_validate(response.json())

    async def post_calculo_portabilidade_refin(
        self, calculation_dto: CalculationPortRefinRequestDto
    ) -> CalculationPortRefinResponseDto:
        response = await self.api.post_calculo_portabilidade_refin(calculation_dto)
        return CalculationPortRefinResponseDto.model_validate(response.json())

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]:
        return await self._list_from_api(
            lambda: self.api.list_safra_tables(convenio_id),
            SafraTablesDto,
        )

    async def list_interest_table_bands(
        self, table_id: int
    ) -> List[SafraInterestTableBandDto]:
        return await self._list_from_api(
            lambda: self.api.list_interest_table_bands(table_id),
            SafraInterestTableBandDto,
        )

    async def list_proposals(
        self, query_dto: ProposalListQueryDto
    ) -> List[ProposalListItemDto]:
        return await self._list_from_api(
            lambda: self.api.list_proposals(query_dto),
            ProposalListItemDto,
        )

    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto:
        response = await self.api.post_safra_proposal(proposal_dto)
        return ProposalResponseDto.model_validate(response.json())

    async def post_proposal_attachment(
        self, proposal_id: int, attachment_dto: ProposalAttachmentDto
    ) -> None:
        await self.api.post_proposal_attachment(proposal_id, attachment_dto)

    async def list_leads(self) -> List[LeadDto]:
        return await self._list_from_api(self.api.list_leads, LeadDto)

    async def download_leads_csv(self) -> bytes:
        response = await self.api.download_leads_csv()
        return response.content

    async def upload_leads_return(self, items: List[LeadReturnUploadItemDto]) -> None:
        await self.api.upload_leads_return(items)

    async def upload_leads_return_file(
        self, file_content: bytes, filename: str
    ) -> None:
        await self.api.upload_leads_return_file(file_content, filename)

    async def get_proposal_formalization_link(
        self, query_dto: FormalizationLinkQueryDto
    ) -> List[FormalizationLinkResponseDto]:
        return await self._list_from_api(
            lambda: self.api.get_proposal_formalization_link(query_dto),
            FormalizationLinkResponseDto,
        )

    async def get_proposal_flow(self, proposal_id: int) -> List[ProposalFlowStepDto]:
        return await self._list_from_api(
            lambda: self.api.get_proposal_flow(proposal_id),
            ProposalFlowStepDto,
        )

    async def get_formalization_tracking(
        self, proposal_id: int
    ) -> List[FormalizationTrackingDto]:
        return await self._list_from_api(
            lambda: self.api.get_formalization_tracking(proposal_id),
            FormalizationTrackingDto,
        )

    async def approve_paradinha(self, proposal_id: int) -> ParadinhaResponseDto:
        response = await self.api.approve_paradinha(proposal_id)
        return ParadinhaResponseDto.model_validate(response.json())

    async def cancel_paradinha(self, proposal_id: int) -> ParadinhaResponseDto:
        response = await self.api.cancel_paradinha(proposal_id)
        return ParadinhaResponseDto.model_validate(response.json())

    async def list_agencies(self) -> List[SafraAgencyDto]:
        return await self._list_from_api(self.api.list_agencies, SafraAgencyDto)

    async def list_positions(self, profession_id: int) -> List[SafraPositionDto]:
        return await self._list_from_api(
            lambda: self.api.list_positions(profession_id),
            SafraPositionDto,
        )

    async def list_employment_bonds(
        self, convenio_id: int
    ) -> List[SafraEmploymentBondDto]:
        return await self._list_from_api(
            lambda: self.api.list_employment_bonds(convenio_id),
            SafraEmploymentBondDto,
        )

    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodyDTO]:
        return await self._list_from_api(
            lambda: self.api.get_employing_bodies(financial_agreement_id),
            SafraEmployingBodyDTO,
        )

    async def get_professions(
        self, financial_agreement_id: int
    ) -> List[SafraProfessionsDTO]:
        return await self._list_from_api(
            lambda: self.api.get_professions(financial_agreement_id),
            SafraProfessionsDTO,
        )

    async def get_legal_regime(
        self, financial_agreement_id: int
    ) -> List[LegalRegimeDTO]:
        return await self._list_from_api(
            lambda: self.api.get_legal_regime(financial_agreement_id),
            LegalRegimeDTO,
        )

    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> List[EmployeeSituationDTO]:
        return await self._list_from_api(
            lambda: self.api.get_employee_situation(
                financial_agreement_id,
                legal_regime_id,
            ),
            EmployeeSituationDTO,
        )

    async def get_contracts_registration_by_cpf(
        self, cpf: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_registration_by_cpf(cpf),
            ContractRegistrationDataDto,
        )

    async def get_contracts_registration_by_date(
        self, proposal_date: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_registration_by_date(proposal_date),
            ContractRegistrationDataDto,
        )

    async def get_contracts_registration_by_proposal(
        self, proposal_number: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_registration_by_proposal(proposal_number),
            ContractRegistrationDataDto,
        )

    async def get_contracts_loan_by_cpf(self, cpf: str) -> List[ContractLoanDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_loan_by_cpf(cpf),
            ContractLoanDto,
        )

    async def get_contracts_loan_by_date(
        self, proposal_date: str
    ) -> List[ContractLoanDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_loan_by_date(proposal_date),
            ContractLoanDto,
        )

    async def get_contracts_loan_by_proposal(
        self, proposal_number: str
    ) -> List[ContractLoanDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_loan_by_proposal(proposal_number),
            ContractLoanDto,
        )

    async def get_contracts_financial_by_cpf(
        self, cpf: str
    ) -> List[ContractFinancialDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_financial_by_cpf(cpf),
            ContractFinancialDto,
        )

    async def get_contracts_financial_by_date(
        self, proposal_date: str
    ) -> List[ContractFinancialDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_financial_by_date(proposal_date),
            ContractFinancialDto,
        )

    async def get_contracts_financial_by_proposal(
        self, proposal_number: str
    ) -> List[ContractFinancialDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_financial_by_proposal(proposal_number),
            ContractFinancialDto,
        )

    async def get_contracts_status_by_cpf(self, cpf: str) -> List[ContractStatusDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_status_by_cpf(cpf),
            ContractStatusDto,
        )

    async def get_contracts_status_by_date(
        self, proposal_date: str
    ) -> List[ContractStatusDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_status_by_date(proposal_date),
            ContractStatusDto,
        )

    async def get_contracts_status_by_proposal(
        self, proposal_number: str
    ) -> List[ContractStatusDto]:
        return await self._list_from_api(
            lambda: self.api.get_contracts_status_by_proposal(proposal_number),
            ContractStatusDto,
        )
