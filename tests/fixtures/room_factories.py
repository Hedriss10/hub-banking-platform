from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.rooms import RoomDTO


def build_room_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    name: str = 'Room Test',
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    is_deleted: bool = False,
) -> RoomDTO:
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    if updated_at is None:
        updated_at = created_at
    return RoomDTO(
        id=id or uuid4(),
        name=name,
        created_at=created_at,
        updated_at=updated_at,
        is_deleted=is_deleted,
    )
