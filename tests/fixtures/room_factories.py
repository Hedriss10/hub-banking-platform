from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.dtos.rooms import RoomDTO
from src.domain.dtos.rooms_employee import RoomEmployeeDTO, RoomEmployeeListDTO


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


def build_room_employee_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    room_id: UUID | None = None,
    employee_id: UUID | None = None,
) -> RoomEmployeeDTO:
    return RoomEmployeeDTO(
        id=id or uuid4(),
        room_id=room_id or uuid4(),
        employee_id=employee_id or uuid4(),
    )


def build_room_employee_list_dto(
    *,
    id: UUID | None = None,  # noqa: A001
    room_id: UUID | None = None,
    employee_id: UUID | None = None,
    first_name: str = 'Maria',
    last_name: str = 'Silva',
) -> RoomEmployeeListDTO:
    return RoomEmployeeListDTO(
        id=id or uuid4(),
        room_id=room_id or uuid4(),
        employee_id=employee_id or uuid4(),
        first_name=first_name,
        last_name=last_name,
    )
