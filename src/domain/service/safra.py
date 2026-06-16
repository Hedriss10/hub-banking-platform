from typing import List

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

    async def get_operational_guide(self, convenio_id: int) -> SafraOperationalGuideDto:
        return await self._safra_repository.get_operational_guide(convenio_id)

    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]:
        return await self._safra_repository.post_credit_lighthouse(
            credit_lighthouse_dto
        )

    async def post_calculo_novo(
        self, calculation_dto: CalculationRequestDto
    ) -> CalculationResponseDto:
        return await self._safra_repository.post_calculo_novo(calculation_dto)

    async def post_calculo_refin(
        self, calculation_dto: CalculationRefinRequestDto
    ) -> CalculationResponseDto:
        return await self._safra_repository.post_calculo_refin(calculation_dto)

    async def post_calculo_portabilidade(
        self, calculation_dto: CalculationPortabilityRequestDto
    ) -> CalculationResponseDto:
        return await self._safra_repository.post_calculo_portabilidade(calculation_dto)

    async def post_calculo_portabilidade_refin(
        self, calculation_dto: CalculationPortRefinRequestDto
    ) -> CalculationPortRefinResponseDto:
        return await self._safra_repository.post_calculo_portabilidade_refin(
            calculation_dto
        )

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]:
        return await self._safra_repository.list_safra_tables(convenio_id)

    async def list_interest_table_bands(
        self, table_id: int
    ) -> List[SafraInterestTableBandDto]:
        return await self._safra_repository.list_interest_table_bands(table_id)

    async def list_proposals(
        self, query_dto: ProposalListQueryDto
    ) -> List[ProposalListItemDto]:
        return await self._safra_repository.list_proposals(query_dto)

    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto:
        return await self._safra_repository.post_safra_proposal(proposal_dto)

    async def post_proposal_attachment(
        self, proposal_id: int, attachment_dto: ProposalAttachmentDto
    ) -> None:
        await self._safra_repository.post_proposal_attachment(
            proposal_id, attachment_dto
        )

    async def list_leads(self) -> List[LeadDto]:
        return await self._safra_repository.list_leads()

    async def download_leads_csv(self) -> bytes:
        return await self._safra_repository.download_leads_csv()

    async def upload_leads_return(self, items: List[LeadReturnUploadItemDto]) -> None:
        await self._safra_repository.upload_leads_return(items)

    async def upload_leads_return_file(
        self, file_content: bytes, filename: str
    ) -> None:
        await self._safra_repository.upload_leads_return_file(file_content, filename)

    async def get_proposal_formalization_link(
        self, query_dto: FormalizationLinkQueryDto
    ) -> List[FormalizationLinkResponseDto]:
        return await self._safra_repository.get_proposal_formalization_link(query_dto)

    async def get_proposal_flow(self, proposal_id: int) -> List[ProposalFlowStepDto]:
        return await self._safra_repository.get_proposal_flow(proposal_id)

    async def get_formalization_tracking(
        self, proposal_id: int
    ) -> List[FormalizationTrackingDto]:
        return await self._safra_repository.get_formalization_tracking(proposal_id)

    async def approve_paradinha(self, proposal_id: int) -> ParadinhaResponseDto:
        return await self._safra_repository.approve_paradinha(proposal_id)

    async def cancel_paradinha(self, proposal_id: int) -> ParadinhaResponseDto:
        return await self._safra_repository.cancel_paradinha(proposal_id)

    async def list_agencies(self) -> List[SafraAgencyDto]:
        return await self._safra_repository.list_agencies()

    async def list_positions(self, profession_id: int) -> List[SafraPositionDto]:
        return await self._safra_repository.list_positions(profession_id)

    async def list_employment_bonds(
        self, convenio_id: int
    ) -> List[SafraEmploymentBondDto]:
        return await self._safra_repository.list_employment_bonds(convenio_id)

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

    async def get_contracts_registration_by_cpf(
        self, cpf: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._safra_repository.get_contracts_registration_by_cpf(cpf)

    async def get_contracts_registration_by_date(
        self, proposal_date: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._safra_repository.get_contracts_registration_by_date(
            proposal_date
        )

    async def get_contracts_registration_by_proposal(
        self, proposal_number: str
    ) -> List[ContractRegistrationDataDto]:
        return await self._safra_repository.get_contracts_registration_by_proposal(
            proposal_number
        )

    async def get_contracts_loan_by_cpf(self, cpf: str) -> List[ContractLoanDto]:
        return await self._safra_repository.get_contracts_loan_by_cpf(cpf)

    async def get_contracts_loan_by_date(
        self, proposal_date: str
    ) -> List[ContractLoanDto]:
        return await self._safra_repository.get_contracts_loan_by_date(proposal_date)

    async def get_contracts_loan_by_proposal(
        self, proposal_number: str
    ) -> List[ContractLoanDto]:
        return await self._safra_repository.get_contracts_loan_by_proposal(
            proposal_number
        )

    async def get_contracts_financial_by_cpf(
        self, cpf: str
    ) -> List[ContractFinancialDto]:
        return await self._safra_repository.get_contracts_financial_by_cpf(cpf)

    async def get_contracts_financial_by_date(
        self, proposal_date: str
    ) -> List[ContractFinancialDto]:
        return await self._safra_repository.get_contracts_financial_by_date(
            proposal_date
        )

    async def get_contracts_financial_by_proposal(
        self, proposal_number: str
    ) -> List[ContractFinancialDto]:
        return await self._safra_repository.get_contracts_financial_by_proposal(
            proposal_number
        )

    async def get_contracts_status_by_cpf(self, cpf: str) -> List[ContractStatusDto]:
        return await self._safra_repository.get_contracts_status_by_cpf(cpf)

    async def get_contracts_status_by_date(
        self, proposal_date: str
    ) -> List[ContractStatusDto]:
        return await self._safra_repository.get_contracts_status_by_date(proposal_date)

    async def get_contracts_status_by_proposal(
        self, proposal_number: str
    ) -> List[ContractStatusDto]:
        return await self._safra_repository.get_contracts_status_by_proposal(
            proposal_number
        )
