from typing import List
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, HTTPException, UploadFile, status

from src.core.config.settings import get_settings
from src.core.exceptions.custom import SafraBatchCsvValidationError
from src.domain.dtos.safra import BankerResponse, MargemBpoDto, TokenResponse
from src.domain.dtos.safra_credit_ligth_house import (
    CreditLighthouseDto,
    CreditLighthouseResponse,
)
from src.domain.dtos.safra_proposal import ProposalDto
from src.domain.use_case.safra import SafraUseCase
from src.domain.use_case.safra_batch_search import SafraBatchSearchUseCase
from src.infrastructure.redis.safra_batch_job_store import job_get, job_save
from src.infrastructure.utils.safra_batch_export_csv import (
    encode_safra_batch_search_export_csv,
)
from src.infrastructure.workers.processing_batch_safra import run_safra_batch_job
from src.infrastructure.workers.safra_batch_csv import parse_safra_batch_csv
from src.interface.api.v2.schemas.safra import (
    BankerOutSchema,
    MargemBpoInSchema,
    MargemBpoOutSchema,
    SafraBatchJobIdsOutSchema,
    SafraBatchJobStatusOutSchema,
    SafraBatchUploadOutSchema,
    TokenOutSchema,
)
from src.interface.api.v2.schemas.safra_credit_ligth_house import (
    CreditLighthouseInSchema,
    CreditLighthouseOutSchema,
)
from src.interface.api.v2.schemas.safra_employing_body import SafraEmployingBodySchema
from src.interface.api.v2.schemas.safra_financial_agreements import (
    FinancialAgreementOutSchema,
)
from src.interface.api.v2.schemas.safra_professions import SafraProfessionsSchema
from src.interface.api.v2.schemas.safra_proposal import (
    ProposalResponseSchema,
    ProposalSchema,
)
from src.interface.api.v2.schemas.safra_regime_legal import SafraRegimeLegalSchema
from src.interface.api.v2.schemas.safra_tables import SafraTablesOutSchema


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
        return [
            FinancialAgreementOutSchema.model_validate(
                financial_agreement.model_dump(),
            )
            for financial_agreement in financial_agreements
        ]

    async def post_credit_lighthouse(
        self, body: CreditLighthouseInSchema
    ) -> List[CreditLighthouseOutSchema]:
        dto = CreditLighthouseDto.model_validate(body.model_dump())
        items = await self._safra_use_case.post_credit_lighthouse(dto)
        return [_credit_lighthouse_to_schema(row) for row in items]

    async def list_safra_tables(self, convenio_id: int) -> List[SafraTablesOutSchema]:
        safra_tables = await self._safra_use_case.list_safra_tables(convenio_id)
        return [
            SafraTablesOutSchema.model_validate(safra_table.model_dump())
            for safra_table in safra_tables
        ]

    async def post_safra_proposal(self, body: ProposalSchema) -> ProposalResponseSchema:
        dto = ProposalDto.model_validate(body.model_dump())
        item = await self._safra_use_case.post_safra_proposal(dto)
        return ProposalResponseSchema.model_validate(item.model_dump(mode='json'))

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
