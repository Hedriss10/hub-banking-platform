from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO


class SafraBatchSearchRepository(ABC):
    @abstractmethod
    async def list_distinct_batch_job_ids(self) -> Sequence[UUID]: ...

    @abstractmethod
    async def list_rows_for_batch_job(
        self,
        batch_job_id: UUID,
    ) -> Sequence[SafraBatchSearchExportRowDTO]: ...

    @abstractmethod
    async def delete_rows_for_batch_job(self, batch_job_id: UUID) -> int: ...
