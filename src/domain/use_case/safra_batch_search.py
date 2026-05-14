from collections.abc import Sequence
from uuid import UUID

from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.domain.exceptions.safra_batch_search import SafraBatchSearchNotFoundException
from src.domain.repositories.safra_batch_search import SafraBatchSearchRepository


class SafraBatchSearchUseCase:
    """Leituras persistidas dos resultados de batch Safra (Postgres)."""

    def __init__(self, repository: SafraBatchSearchRepository) -> None:
        self._repository = repository

    async def list_distinct_batch_job_ids(self) -> Sequence[UUID]:
        batch_ids = await self._repository.list_distinct_batch_job_ids()
        return list(batch_ids)

    async def list_rows_for_export(
        self,
        batch_job_id: UUID,
    ) -> Sequence[SafraBatchSearchExportRowDTO]:
        rows = await self._repository.list_rows_for_batch_job(batch_job_id)
        if not rows:
            raise SafraBatchSearchNotFoundException()
        return rows

    async def delete_persisted_batch_job_rows(self, batch_job_id: UUID) -> None:
        deleted = await self._repository.delete_rows_for_batch_job(batch_job_id)
        if deleted == 0:
            raise SafraBatchSearchNotFoundException(
                message='Nenhuma linha encontrada para esse lote.',
            )
