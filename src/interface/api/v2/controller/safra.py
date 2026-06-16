from datetime import datetime
from typing import List, Optional, TypeVar
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.core.config.settings import get_settings
from src.core.exceptions.custom import SafraBatchCsvValidationError
from src.domain.dtos.safra import BankerResponse, MargemBpoDto, TokenResponse
from src.domain.dtos.safra_calculation import (
    CalculationPortabilityRequestDto,
    CalculationPortRefinRequestDto,
    CalculationRefinRequestDto,
    CalculationRequestDto,
)
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_formalization_link import FormalizationLinkQueryDto
from src.domain.dtos.safra_leads import LeadReturnUploadItemDto
from src.domain.dtos.safra_proposal import ProposalDto
from src.domain.dtos.safra_proposal_attachment import ProposalAttachmentDto
from src.domain.dtos.safra_proposal_tracking import ProposalListQueryDto
from src.domain.use_case.safra import SafraUseCase
from src.domain.use_case.safra_batch_search import SafraBatchSearchUseCase
from src.infrastructure.redis.safra_batch_job_store import job_get, job_save
from src.infrastructure.utils.safra_batch_export_csv import (
    encode_safra_batch_search_export_csv,
)
from src.infrastructure.workers.processing_batch_safra import run_safra_batch_job
from src.infrastructure.workers.safra_batch_csv import parse_safra_batch_csv
from src.interface.api.v2.schemas.employee_situation import EmployeeSituationSchema
from src.interface.api.v2.schemas.safra import (
    BankerOutSchema,
    MargemBpoInSchema,
    MargemBpoOutSchema,
    SafraBatchJobIdsOutSchema,
    SafraBatchJobStatusOutSchema,
    SafraBatchUploadOutSchema,
    TokenOutSchema,
)
from src.interface.api.v2.schemas.safra_calculation import (
    CalculationInSchema,
    CalculationOutSchema,
    CalculationPortabilityInSchema,
    CalculationPortRefinInSchema,
    CalculationPortRefinOutSchema,
    CalculationRefinInSchema,
)
from src.interface.api.v2.schemas.safra_catalog import (
    SafraAgencyOutSchema,
    SafraEmploymentBondOutSchema,
    SafraInterestTableBandOutSchema,
    SafraOperationalGuideOutSchema,
    SafraPositionOutSchema,
)
from src.interface.api.v2.schemas.safra_contracts import (
    ContractFinancialOutSchema,
    ContractLoanOutSchema,
    ContractRegistrationDataOutSchema,
    ContractStatusOutSchema,
)
from src.interface.api.v2.schemas.safra_credit_ligth_house import (
    CreditLighthouseInSchema,
    CreditLighthouseOutSchema,
)
from src.interface.api.v2.schemas.safra_employing_body import SafraEmployingBodySchema
from src.interface.api.v2.schemas.safra_financial_agreements import (
    FinancialAgreementOutSchema,
)
from src.interface.api.v2.schemas.safra_formalization_link import (
    FormalizationLinkOutSchema,
)
from src.interface.api.v2.schemas.safra_leads import (
    LeadOutSchema,
    LeadReturnUploadItemInSchema,
)
from src.interface.api.v2.schemas.safra_professions import SafraProfessionsSchema
from src.interface.api.v2.schemas.safra_proposal import (
    ProposalResponseSchema,
    ProposalSchema,
)
from src.interface.api.v2.schemas.safra_proposal_attachment import (
    ProposalAttachmentInSchema,
)
from src.interface.api.v2.schemas.safra_proposal_tracking import (
    FormalizationTrackingOutSchema,
    ParadinhaOutSchema,
    ProposalFlowStepOutSchema,
    ProposalListItemOutSchema,
)
from src.interface.api.v2.schemas.safra_regime_legal import SafraRegimeLegalSchema
from src.interface.api.v2.schemas.safra_tables import SafraTablesOutSchema

TSchema = TypeVar('TSchema', bound=BaseModel)


def _map_items(items: list, schema_cls: type[TSchema]) -> List[TSchema]:
    return [schema_cls.model_validate(item.model_dump(mode='json')) for item in items]


def _token_to_schema(dto: TokenResponse) -> TokenOutSchema:
    return TokenOutSchema.model_validate(dto.model_dump(mode='json'))


def _banker_to_schema(dto: BankerResponse) -> BankerOutSchema:
    return BankerOutSchema.model_validate(dto.model_dump(mode='json'))


def _credit_lighthouse_to_schema(
    dto: CreditLighthouseResponse,
) -> CreditLighthouseOutSchema:
    return CreditLighthouseOutSchema.model_validate(
        dto.model_dump(mode='json'),
    )


class SafraController:
    def __init__(
        self,
        safra_use_case: SafraUseCase,
        safra_batch_search_use_case: SafraBatchSearchUseCase,
    ) -> None:
        self._safra_use_case = safra_use_case
        self._safra_batch_search_use_case = safra_batch_search_use_case

    async def get_token(self) -> TokenOutSchema:
        dto = await self._safra_use_case.get_token()
        return _token_to_schema(dto)

    async def list_banks(self) -> List[BankerOutSchema]:
        items = await self._safra_use_case.get_bankers()
        return [_banker_to_schema(row) for row in items]

    async def consult_margem_bpo(self, body: MargemBpoInSchema) -> MargemBpoOutSchema:
        dto = MargemBpoDto.model_validate(body.model_dump())
        out = await self._safra_use_case.get_margem_bpo(dto)
        return MargemBpoOutSchema.model_validate(out.model_dump(mode='json'))

    async def upload_batch_search_csv(
        self,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> SafraBatchUploadOutSchema:
        settings = get_settings()
        if not settings.REDIS_URL:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    'REDIS_URL não configurado — batch em segundo plano indisponível.'
                ),
            )

        content = await file.read()
        try:
            rows = parse_safra_batch_csv(content)
        except SafraBatchCsvValidationError as exc:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail={'messages': exc.messages},
            ) from exc

        job_id = uuid4()
        await job_save(
            job_id,
            {
                'status': 'queued',
                'total_rows': len(rows),
                'processed_rows': 0,
                'failed_rows': 0,
                'detail': None,
            },
        )
        payload = [row.model_dump(mode='json') for row in rows]
        background_tasks.add_task(run_safra_batch_job, job_id, payload)
        return SafraBatchUploadOutSchema(
            job_id=job_id,
            status='queued',
            total_rows=len(rows),
        )

    async def get_batch_job_status(self, job_id: UUID) -> SafraBatchJobStatusOutSchema:
        settings = get_settings()
        if not settings.REDIS_URL:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    'REDIS_URL não configurado — batch em segundo plano indisponível.'
                ),
            )

        state = await job_get(job_id)
        if state is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail='Job não encontrado',
            )

        return SafraBatchJobStatusOutSchema(
            job_id=job_id,
            status=str(state['status']),
            total_rows=int(state['total_rows']),
            processed_rows=int(state['processed_rows']),
            failed_rows=int(state['failed_rows']),
            detail=state.get('detail'),
        )

    async def list_persisted_batch_job_ids(self) -> SafraBatchJobIdsOutSchema:
        ids = await self._safra_batch_search_use_case.list_distinct_batch_job_ids()
        return SafraBatchJobIdsOutSchema(batch_job_ids=list(ids))

    async def export_batch_job_results_csv(self, batch_job_id: UUID) -> bytes:
        rows = await self._safra_batch_search_use_case.list_rows_for_export(
            batch_job_id,
        )
        return encode_safra_batch_search_export_csv(list(rows))

    async def delete_batch_job_search_records(self, batch_job_id: UUID) -> None:
        await self._safra_batch_search_use_case.delete_persisted_batch_job_rows(
            batch_job_id,
        )

    async def list_financial_agreements(self) -> List[FinancialAgreementOutSchema]:
        financial_agreements = await self._safra_use_case.get_financial_agreements()
        return _map_items(financial_agreements, FinancialAgreementOutSchema)

    async def get_operational_guide(
        self, convenio_id: int
    ) -> SafraOperationalGuideOutSchema:
        item = await self._safra_use_case.get_operational_guide(convenio_id)
        return SafraOperationalGuideOutSchema.model_validate(
            item.model_dump(mode='json'),
        )

    async def post_credit_lighthouse(
        self, body: CreditLighthouseInSchema
    ) -> List[CreditLighthouseOutSchema]:
        dto = CreditLighthouseDto.model_validate(body.model_dump())
        items = await self._safra_use_case.post_credit_lighthouse(dto)
        return [_credit_lighthouse_to_schema(row) for row in items]

    async def post_calculo_novo(
        self, body: CalculationInSchema
    ) -> CalculationOutSchema:
        dto = CalculationRequestDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_calculo_novo(dto)
        return CalculationOutSchema.model_validate(item.model_dump(mode='json'))

    async def post_calculo_refin(
        self, body: CalculationRefinInSchema
    ) -> CalculationOutSchema:
        dto = CalculationRefinRequestDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_calculo_refin(dto)
        return CalculationOutSchema.model_validate(item.model_dump(mode='json'))

    async def post_calculo_portabilidade(
        self, body: CalculationPortabilityInSchema
    ) -> CalculationOutSchema:
        dto = CalculationPortabilityRequestDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_calculo_portabilidade(dto)
        return CalculationOutSchema.model_validate(item.model_dump(mode='json'))

    async def post_calculo_portabilidade_refin(
        self, body: CalculationPortRefinInSchema
    ) -> CalculationPortRefinOutSchema:
        dto = CalculationPortRefinRequestDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_calculo_portabilidade_refin(dto)
        return CalculationPortRefinOutSchema.model_validate(
            item.model_dump(mode='json'),
        )

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesOutSchema]:
        safra_tables = await self._safra_use_case.list_safra_tables(convenio_id)
        return _map_items(safra_tables, SafraTablesOutSchema)

    async def list_interest_table_bands(
        self, table_id: int
    ) -> List[SafraInterestTableBandOutSchema]:
        items = await self._safra_use_case.list_interest_table_bands(table_id)
        return _map_items(items, SafraInterestTableBandOutSchema)

    async def list_proposals(
        self,
        id_proposta: Optional[int] = None,
        id_cliente: Optional[int] = None,
        dt_inicio: Optional[datetime] = None,
        dt_fim: Optional[datetime] = None,
        id_convenio: Optional[int] = None,
        id_situacao: Optional[int] = None,
        id_tp_produto: Optional[int] = None,
    ) -> List[ProposalListItemOutSchema]:
        query_dto = ProposalListQueryDto(
            id_proposta=id_proposta,
            id_cliente=id_cliente,
            dt_inicio=dt_inicio,
            dt_fim=dt_fim,
            id_convenio=id_convenio,
            id_situacao=id_situacao,
            id_tp_produto=id_tp_produto,
        )
        items = await self._safra_use_case.list_proposals(query_dto)
        return _map_items(items, ProposalListItemOutSchema)

    async def post_safra_proposal(self, body: ProposalSchema) -> ProposalResponseSchema:
        dto = ProposalDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_safra_proposal(dto)
        return ProposalResponseSchema.model_validate(item.model_dump(mode='json'))

    async def post_proposal_attachment(
        self, proposal_id: int, body: ProposalAttachmentInSchema
    ) -> None:
        dto = ProposalAttachmentDto.model_validate(body.model_dump())
        await self._safra_use_case.post_proposal_attachment(proposal_id, dto)

    async def list_leads(self) -> List[LeadOutSchema]:
        items = await self._safra_use_case.list_leads()
        return _map_items(items, LeadOutSchema)

    async def download_leads_csv(self) -> bytes:
        return await self._safra_use_case.download_leads_csv()

    async def upload_leads_return(
        self, body: List[LeadReturnUploadItemInSchema]
    ) -> None:
        items = [
            LeadReturnUploadItemDto.model_validate(row.model_dump()) for row in body
        ]
        await self._safra_use_case.upload_leads_return(items)

    async def upload_leads_return_file(
        self, file_content: bytes, filename: str
    ) -> None:
        await self._safra_use_case.upload_leads_return_file(file_content, filename)

    async def get_proposal_formalization_link(
        self,
        id_proposta: Optional[int] = None,
        id_cliente: Optional[int] = None,
        dt_inicio: Optional[datetime] = None,
        dt_fim: Optional[datetime] = None,
        id_convenio: Optional[int] = None,
    ) -> List[FormalizationLinkOutSchema]:
        query_dto = FormalizationLinkQueryDto(
            idProposta=id_proposta,
            idCliente=id_cliente,
            dtInicio=dt_inicio,
            dtFim=dt_fim,
            idConvenio=id_convenio,
        )
        items = await self._safra_use_case.get_proposal_formalization_link(query_dto)
        return [
            FormalizationLinkOutSchema.model_validate(item.model_dump(mode='json'))
            for item in items
        ]

    async def get_proposal_flow(
        self, proposal_id: int
    ) -> List[ProposalFlowStepOutSchema]:
        items = await self._safra_use_case.get_proposal_flow(proposal_id)
        return _map_items(items, ProposalFlowStepOutSchema)

    async def get_formalization_tracking(
        self, proposal_id: int
    ) -> List[FormalizationTrackingOutSchema]:
        items = await self._safra_use_case.get_formalization_tracking(proposal_id)
        return _map_items(items, FormalizationTrackingOutSchema)

    async def approve_paradinha(self, proposal_id: int) -> ParadinhaOutSchema:
        item = await self._safra_use_case.approve_paradinha(proposal_id)
        return ParadinhaOutSchema.model_validate(item.model_dump(mode='json'))

    async def cancel_paradinha(self, proposal_id: int) -> ParadinhaOutSchema:
        item = await self._safra_use_case.cancel_paradinha(proposal_id)
        return ParadinhaOutSchema.model_validate(item.model_dump(mode='json'))

    async def list_agencies(self) -> List[SafraAgencyOutSchema]:
        items = await self._safra_use_case.list_agencies()
        return _map_items(items, SafraAgencyOutSchema)

    async def list_positions(self, profession_id: int) -> List[SafraPositionOutSchema]:
        items = await self._safra_use_case.list_positions(profession_id)
        return _map_items(items, SafraPositionOutSchema)

    async def list_employment_bonds(
        self, convenio_id: int
    ) -> List[SafraEmploymentBondOutSchema]:
        items = await self._safra_use_case.list_employment_bonds(convenio_id)
        return _map_items(items, SafraEmploymentBondOutSchema)

    async def get_contracts_registration_by_cpf(
        self, cpf: str
    ) -> List[ContractRegistrationDataOutSchema]:
        items = await self._safra_use_case.get_contracts_registration_by_cpf(cpf)
        return _map_items(items, ContractRegistrationDataOutSchema)

    async def get_contracts_registration_by_date(
        self, proposal_date: str
    ) -> List[ContractRegistrationDataOutSchema]:
        items = await self._safra_use_case.get_contracts_registration_by_date(
            proposal_date,
        )
        return _map_items(items, ContractRegistrationDataOutSchema)

    async def get_contracts_registration_by_proposal(
        self, proposal_number: str
    ) -> List[ContractRegistrationDataOutSchema]:
        items = await self._safra_use_case.get_contracts_registration_by_proposal(
            proposal_number,
        )
        return _map_items(items, ContractRegistrationDataOutSchema)

    async def get_contracts_loan_by_cpf(self, cpf: str) -> List[ContractLoanOutSchema]:
        items = await self._safra_use_case.get_contracts_loan_by_cpf(cpf)
        return _map_items(items, ContractLoanOutSchema)

    async def get_contracts_loan_by_date(
        self, proposal_date: str
    ) -> List[ContractLoanOutSchema]:
        items = await self._safra_use_case.get_contracts_loan_by_date(proposal_date)
        return _map_items(items, ContractLoanOutSchema)

    async def get_contracts_loan_by_proposal(
        self, proposal_number: str
    ) -> List[ContractLoanOutSchema]:
        items = await self._safra_use_case.get_contracts_loan_by_proposal(
            proposal_number,
        )
        return _map_items(items, ContractLoanOutSchema)

    async def get_contracts_financial_by_cpf(
        self, cpf: str
    ) -> List[ContractFinancialOutSchema]:
        items = await self._safra_use_case.get_contracts_financial_by_cpf(cpf)
        return _map_items(items, ContractFinancialOutSchema)

    async def get_contracts_financial_by_date(
        self, proposal_date: str
    ) -> List[ContractFinancialOutSchema]:
        items = await self._safra_use_case.get_contracts_financial_by_date(
            proposal_date
        )
        return _map_items(items, ContractFinancialOutSchema)

    async def get_contracts_financial_by_proposal(
        self, proposal_number: str
    ) -> List[ContractFinancialOutSchema]:
        items = await self._safra_use_case.get_contracts_financial_by_proposal(
            proposal_number,
        )
        return _map_items(items, ContractFinancialOutSchema)

    async def get_contracts_status_by_cpf(
        self, cpf: str
    ) -> List[ContractStatusOutSchema]:
        items = await self._safra_use_case.get_contracts_status_by_cpf(cpf)
        return _map_items(items, ContractStatusOutSchema)

    async def get_contracts_status_by_date(
        self, proposal_date: str
    ) -> List[ContractStatusOutSchema]:
        items = await self._safra_use_case.get_contracts_status_by_date(proposal_date)
        return _map_items(items, ContractStatusOutSchema)

    async def get_contracts_status_by_proposal(
        self, proposal_number: str
    ) -> List[ContractStatusOutSchema]:
        items = await self._safra_use_case.get_contracts_status_by_proposal(
            proposal_number,
        )
        return _map_items(items, ContractStatusOutSchema)

    async def get_employing_bodies(
        self, financial_agreement_id: int
    ) -> List[SafraEmployingBodySchema]:
        items = await self._safra_use_case.get_employing_bodies(financial_agreement_id)
        return [
            SafraEmployingBodySchema.model_validate(item.model_dump()) for item in items
        ]

    async def get_professions(
        self, financial_agreement_id: int
    ) -> List[SafraProfessionsSchema]:
        items = await self._safra_use_case.get_professions(financial_agreement_id)
        return [
            SafraProfessionsSchema.model_validate(item.model_dump()) for item in items
        ]

    async def get_legal_regime(
        self, financial_agreement_id: int
    ) -> List[SafraRegimeLegalSchema]:
        items = await self._safra_use_case.get_legal_regime(financial_agreement_id)
        return [
            SafraRegimeLegalSchema.model_validate(item.model_dump()) for item in items
        ]

    async def get_employee_situation(
        self, financial_agreement_id: int, legal_regime_id: int
    ) -> List[EmployeeSituationSchema]:
        items = await self._safra_use_case.get_employee_situation(
            financial_agreement_id, legal_regime_id
        )
        return [
            EmployeeSituationSchema.model_validate(item.model_dump()) for item in items
        ]
