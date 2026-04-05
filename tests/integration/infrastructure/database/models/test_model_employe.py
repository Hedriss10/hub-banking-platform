import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models.common.role import RoleStatus
from src.infrastructure.database.models.employee import Employee

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]


async def test_employee_model_can_be_created(
    async_session: AsyncSession, unique_employee_email: str
):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    assert employee.id is not None


async def test_employee_model_can_be_retrieved(
    async_session: AsyncSession, unique_employee_email: str
):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    retrieved_employee = await async_session.get(Employee, employee.id)
    assert retrieved_employee is not None


async def test_employee_model_can_be_updated(
    async_session: AsyncSession, unique_employee_email: str
):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    employee.first_name = 'Jane'
    await async_session.commit()
    updated_employee = await async_session.get(Employee, employee.id)
    assert updated_employee.first_name == 'Jane'


async def test_employee_model_can_be_listed(
    async_session: AsyncSession, unique_employee_email: str
):
    employees = [
        Employee(
            first_name='John',
            last_name='Doe',
            role=RoleStatus.ADMIN,
            email=unique_employee_email,
            password='password',
        ),
    ]
    async_session.add_all(employees)
    await async_session.commit()
    listed_employees = await async_session.execute(
        select(Employee).where(Employee.email == unique_employee_email)
    )
    assert len(listed_employees.scalars().all()) == len(employees)


async def test_employee_model_can_be_filtered(
    async_session: AsyncSession, unique_employee_email: str
):
    employees = [
        Employee(
            first_name='John',
            last_name='Doe',
            role=RoleStatus.ADMIN,
            email=unique_employee_email,
            password='password',
        ),
    ]
    async_session.add_all(employees)
    await async_session.commit()
    filtered_employees = await async_session.execute(
        select(Employee).where(
            Employee.first_name.__eq__('John'),
            Employee.email.__eq__(unique_employee_email),
        )
    )
    rows = filtered_employees.scalars().all()
    assert len(rows) == 1
    assert rows[0].first_name == 'John'


async def test_employee_soft_delete(
    async_session: AsyncSession, unique_employee_email: str
):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    employee.is_deleted = True
    await async_session.commit()
    deleted_employee = await async_session.get(Employee, employee.id)
    assert deleted_employee is not None
    assert deleted_employee.is_deleted is True


async def test_employee_hard_delete(
    async_session: AsyncSession, unique_employee_email: str
):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        role=RoleStatus.ADMIN,
        email=unique_employee_email,
        password='password',
    )
    async_session.add(employee)
    await async_session.commit()
    await async_session.delete(employee)
    await async_session.commit()
    deleted_employee = await async_session.get(Employee, employee.id)
    assert deleted_employee is None
