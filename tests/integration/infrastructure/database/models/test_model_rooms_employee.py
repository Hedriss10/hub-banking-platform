import random

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models.common.role import RoleStatus
from src.infrastructure.database.models.employee import Employee
from src.infrastructure.database.models.rooms import RoomsModel
from src.infrastructure.database.models.rooms_employee import RoomsEmployee

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]


async def test_rooms_employee_model_can_be_created(
    async_session: AsyncSession,
    unique_employee_email: str,
):
    employee = Employee(
        first_name='Room',
        last_name='Member',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        document=f'{random.randint(100000000000, 999999999999)}',
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    await async_session.refresh(employee)

    room = RoomsModel(name='Test Room', created_by=employee.id)
    async_session.add(room)
    await async_session.commit()
    await async_session.refresh(room)

    rooms_employee = RoomsEmployee(
        room_id=room.id,
        employee_id=employee.id,
    )
    async_session.add(rooms_employee)
    await async_session.commit()
    assert rooms_employee.id is not None
