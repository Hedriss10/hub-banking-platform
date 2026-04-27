from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.bankers import BankerOutDto


def build_banker_out_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    name: str = 'Banco Teste',
    created_at: datetime | None = None,
) -> BankerOutDto:
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    return BankerOutDto(
        id=id or uuid4(),
        name=name,
        created_at=created_at,
    )
