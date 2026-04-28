from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.financial_agreements import FinancialAgreementsOutDto


def build_financial_agreement_out_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    name: str = 'Test agreement',
    bankers_id: UUID | None = None,
    created_by: UUID | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    is_deleted: bool = False,
) -> FinancialAgreementsOutDto:
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    if updated_at is None:
        updated_at = datetime.now(timezone.utc)
    return FinancialAgreementsOutDto(
        id=id or uuid4(),
        name=name,
        bankers_id=bankers_id or uuid4(),
        created_at=created_at,
        updated_at=updated_at,
        is_deleted=is_deleted,
        created_by=created_by or uuid4(),
    )
