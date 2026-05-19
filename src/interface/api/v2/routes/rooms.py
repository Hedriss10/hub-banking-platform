from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Path, Response, status

from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.rooms import RoomsControllerDep
from src.interface.api.v2.schemas.rooms import (
    RoomCreateSchema,
    RoomEmployeeCreateSchema,
    RoomEmployeeListItemSchema,
    RoomEmployeeOutSchema,
    RoomOutSchema,
    RoomUpdateSchema,
)

tags_metadata = {
    'name': 'Rooms',
    'description': ('Rooms management.'),
}


router = APIRouter(
    prefix='/rooms',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=RoomOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create room',
    description=(
        'Create a new room. The creator is taken from the JWT access token '
        '(Authorization: Bearer).'
    ),
)
async def create_room(
    room: RoomCreateSchema,
    controller: RoomsControllerDep,
    employee_id: CurrentEmployeeIdDep,
) -> RoomOutSchema:
    return await controller.create_room(room, employee_id)


@router.get(
    '',
    response_model=List[RoomOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List rooms',
    description='List all rooms that are not logically deleted.',
)
async def list_rooms(
    controller: RoomsControllerDep,
) -> List[RoomOutSchema]:
    return await controller.get_all_rooms()


@router.get(
    '/{room_id}/employees',
    response_model=List[RoomEmployeeListItemSchema],
    status_code=status.HTTP_200_OK,
    summary='List room employees',
    description='List all employees linked to a room.',
)
async def list_room_employees(
    room_id: UUID,
    controller: RoomsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> List[RoomEmployeeListItemSchema]:
    return await controller.get_room_employees(room_id)


@router.post(
    '/{room_id}/employees',
    response_model=RoomEmployeeOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create room employee',
    description='Link an employee to a room. The employee id is sent the request body',
)
async def create_room_employee(
    room_id: UUID,
    room_employee: RoomEmployeeCreateSchema,
    controller: RoomsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> RoomEmployeeOutSchema:
    return await controller.create_room_employee(room_id, room_employee)


@router.delete(
    '/{room_id}/employees/{employee_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete room employee',
    description=(
        'Remove the link between a room and an employee. '
        'The employee id is taken from the URL path; no request body is required.'
    ),
)
async def delete_room_employee(
    room_id: UUID,
    controller: RoomsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
    employee_id: Annotated[
        UUID,
        Path(description='Employee id to remove from the room.'),
    ],
) -> Response:
    await controller.delete_room_employee(room_id, employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    '/{room_id}',
    response_model=RoomOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Get room',
    description='Get a room by id.',
)
async def get_room(
    room_id: UUID,
    controller: RoomsControllerDep,
) -> RoomOutSchema:
    return await controller.get_room_by_id(room_id)


@router.patch(
    '/{room_id}',
    response_model=RoomOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Update room',
    description='Update the room name.',
)
async def update_room(
    room_id: UUID,
    room: RoomUpdateSchema,
    controller: RoomsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> RoomOutSchema:
    return await controller.update_room(room_id, room)


@router.delete(
    '/{room_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete room',
    description='Logical deletion of the room.',
)
async def delete_room(
    room_id: UUID,
    controller: RoomsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.delete_room(room_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
