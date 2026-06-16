from abc import ABC, abstractmethod
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


class SafraRepository(ABC):
    @abstractmethod
    async def get_token(self) -> TokenResponse: ...

    @abstractmethod
    async def get_bankers(self) -> List[BankerResponse]: ...

    @abstractmethod
    async def get_margem_bpo(
        self, margem_bpo_dto: MargemBpoDto
    ) -> MargemBpoOutputDto: ...

    @abstractmethod
    async def get_financial_agreements(self) -> List[FinancialAgreementResponse]: ...

    @abstractmethod
    async def get_operational_guide(
        self, convenio_id: int
    ) -> SafraOperationalGuideDto: ...

    @abstractmethod
    async def post_credit_lighthouse(
        self, credit_lighthouse_dto: CreditLighthouseDto
    ) -> List[CreditLighthouseResponse]: ...

    @abstractmethod
    async def post_calculo_novo(
        self, calculation_dto: CalculationRequestDto
    ) -> CalculationResponseDto: ...

    @abstractmethod
    async def post_calculo_refin(
        self, calculation_dto: CalculationRefinRequestDto
    ) -> CalculationResponseDto: ...

    @abstractmethod
    async def post_calculo_portabilidade(
        self, calculation_dto: CalculationPortabilityRequestDto
    ) -> CalculationResponseDto: ...

    @abstractmethod
    async def post_calculo_portabilidade_refin(
        self, calculation_dto: CalculationPortRefinRequestDto
    ) -> CalculationPortRefinResponseDto: ...

    @abstractmethod
    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesDto]: ...

    @abstractmethod
    async def list_interest_table_bands(
        self, table_id: int
    ) -> List[SafraInterestTableBandDto]: ...

    @abstractmethod
    async def list_proposals(
        self, query_dto: ProposalListQueryDto
    ) -> List[ProposalListItemDto]: ...

    @abstractmethod
    async def post_safra_proposal(
        self, proposal_dto: ProposalDto
    ) -> ProposalResponseDto: ...

    @abstractmethod
    async def post_proposal_attachment(
        self, proposal_id: int, attachment_dto: ProposalAttachmentDto
    ) -> None: ...

    @abstractmethod
    async def list_leads(self) -> List[LeadDto]: ...

    @abstractmethod
    async def download_leads_csv(self) -> bytes: ...

    @abstractmethod
    async def upload_leads_return(
        self, items: List[LeadReturnUploadItemDto]
    ) -> None: ...

    @abstractmethod
    async def upload_leads_return_file(
        self, file_content: bytes, filename: str
    ) -> None: ...

    @abstractmethod
    async def get_proposal_formalization_link(
        self, query_dto: FormalizationLinkQueryDto
    ) -> List[FormalizationLinkResponseDto]: ...

    @abstractmethod
    async def get_proposal_flow(
        self, proposal_id: int
    ) -> List[ProposalFlowStepDto]: ...

    @abstractmethod
    async def get_formalization_tracking(
        self, proposal_id: int
    ) -> List[FormalizationTrackingDto]: ...

    @abstractmethod
    async def approve_paradinha(self, proposal_id: int) -> ParadinhaResponseDto: ...

    @abstractmethod
    async def cancel_paradinha(self, proposal_id: int) -> ParadinhaResponseDto: ...

    @abstractmethod
    async def list_agencies(self) -> List[SafraAgencyDto]: ...

    @abstractmethod
    async def list_positions(self, profession_id: int) -> List[SafraPositionDto]: ...

    @abstractmethod
    async def list_employment_bonds(
        self, convenio_id: int
    ) -> List[SafraEmploymentBondDto]: ...

    @abstractmethod
    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodyDTO]: ...

    @abstractmethod
    async def get_professions(
        self, financial_agreement_id: int
    ) -> List[SafraProfessionsDTO]: ...

    @abstractmethod
    async def get_legal_regime(
        self, financial_agreement_id: int
    ) -> List[LegalRegimeDTO]: ...

    @abstractmethod
    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> List[EmployeeSituationDTO]: ...

    @abstractmethod
    async def get_contracts_registration_by_cpf(
        self, cpf: str
    ) -> List[ContractRegistrationDataDto]: ...

    @abstractmethod
    async def get_contracts_registration_by_date(
        self, proposal_date: str
    ) -> List[ContractRegistrationDataDto]: ...

    @abstractmethod
    async def get_contracts_registration_by_proposal(
        self, proposal_number: str
    ) -> List[ContractRegistrationDataDto]: ...

    @abstractmethod
    async def get_contracts_loan_by_cpf(self, cpf: str) -> List[ContractLoanDto]: ...

    @abstractmethod
    async def get_contracts_loan_by_date(
        self, proposal_date: str
    ) -> List[ContractLoanDto]: ...

    @abstractmethod
    async def get_contracts_loan_by_proposal(
        self, proposal_number: str
    ) -> List[ContractLoanDto]: ...

    @abstractmethod
    async def get_contracts_financial_by_cpf(
        self, cpf: str
    ) -> List[ContractFinancialDto]: ...

    @abstractmethod
    async def get_contracts_financial_by_date(
        self, proposal_date: str
    ) -> List[ContractFinancialDto]: ...

    @abstractmethod
    async def get_contracts_financial_by_proposal(
        self, proposal_number: str
    ) -> List[ContractFinancialDto]: ...

    @abstractmethod
    async def get_contracts_status_by_cpf(
        self, cpf: str
    ) -> List[ContractStatusDto]: ...

    @abstractmethod
    async def get_contracts_status_by_date(
        self, proposal_date: str
    ) -> List[ContractStatusDto]: ...

    @abstractmethod
    async def get_contracts_status_by_proposal(
        self, proposal_number: str
    ) -> List[ContractStatusDto]: ...
