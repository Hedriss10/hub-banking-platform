from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.loan_operation import LoanOperationOutDTO


def build_loan_operation_out_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    name: str = 'Test loan operation',
    created_by: UUID | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    is_deleted: bool = False,
) -> LoanOperationOutDTO:
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    if updated_at is None:
        updated_at = datetime.now(timezone.utc)
    return LoanOperationOutDTO(
        id=id or uuid4(),
        name=name,
        created_at=created_at,
        updated_at=updated_at,
        is_deleted=is_deleted,
        created_by=created_by or uuid4(),
    )
