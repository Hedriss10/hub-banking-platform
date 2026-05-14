from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dtos.safra_batch_search import SafraBatchSearchExportRowDTO
from src.domain.repositories.safra_batch_search import SafraBatchSearchRepository
from src.infrastructure.database.models.safra_batch_search import SafraBatchSearchModel


class SafraBatchSearchPostgresRepository(SafraBatchSearchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_distinct_batch_job_ids(self) -> Sequence[UUID]:
        stmt = (
            select(SafraBatchSearchModel.batch_job_id)
            .where(SafraBatchSearchModel.is_deleted.is_(False))
            .distinct()
            .order_by(SafraBatchSearchModel.batch_job_id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_rows_for_batch_job(
        self,
        batch_job_id: UUID,
    ) -> Sequence[SafraBatchSearchExportRowDTO]:
        stmt = (
            select(SafraBatchSearchModel)
            .where(
                SafraBatchSearchModel.batch_job_id == batch_job_id,
                SafraBatchSearchModel.is_deleted.is_(False),
            )
            .order_by(SafraBatchSearchModel.created_at.asc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [SafraBatchSearchExportRowDTO.model_validate(m) for m in models]

    async def delete_rows_for_batch_job(self, batch_job_id: UUID) -> int:
        stmt = delete(SafraBatchSearchModel).where(
            SafraBatchSearchModel.batch_job_id == batch_job_id,
        )
        result = await self.session.execute(stmt)
        deleted = int(result.rowcount or 0)
        await self.session.commit()
        return deleted
