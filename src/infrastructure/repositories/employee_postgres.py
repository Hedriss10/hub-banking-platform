from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO
from src.domain.repositories.employee import EmployeeRepository
from src.infrastructure.database.models.common.role import RoleStatus
from src.infrastructure.database.models.employee import Employee
from src.infrastructure.database.utils.status_code import is_unique_violation
from src.infrastructure.utils.get_argon import hash_password


class EmployeeRepositoryPostgres(EmployeeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_employee(self, employee: EmployeeCreateDTO) -> EmployeeDTO:
        data = employee.model_dump()
        data['role'] = RoleStatus(data['role'].value)
        data['password'] = hash_password(data['password'])
        employee_db = Employee(**data)
        try:
            self.session.add(employee_db)
            await self.session.commit()
            await self.session.refresh(employee_db)
            return EmployeeDTO.model_validate(employee_db)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                raise DuplicatedException(str(error.orig)) from error
            raise DatabaseException(str(error)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_employee_by_id(self, employee_id: UUID) -> Optional[EmployeeDTO]:
        try:
            statement = select(Employee).where(
                Employee.id.__eq__(employee_id),
                Employee.is_deleted.is_(False),
            )
            result = await self.session.execute(statement)
            employee_db = result.scalar_one_or_none()
            if employee_db is None:
                return None
            return EmployeeDTO.model_validate(employee_db)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_employee(
        self, employee_id: UUID, employee: EmployeeUpdateDTO
    ) -> EmployeeDTO:
        payload = employee.model_dump(exclude_unset=True, exclude_none=True)
        if 'role' in payload:
            payload['role'] = RoleStatus(payload['role'].value)
        if not payload:
            current = await self.get_employee_by_id(employee_id)
            if current is None:
                raise DatabaseException('Funcionário não encontrado')
            return current
        try:
            stmt = (
                update(Employee)
                .where(Employee.id.__eq__(employee_id))
                .where(Employee.is_deleted.is_(False))
                .values(**payload)
                .returning(Employee)
            )
            result = await self.session.execute(stmt)
            employee_db = result.scalar_one_or_none()
            if employee_db is None:
                await self.session.rollback()
                raise DatabaseException('Funcionário não encontrado')
            await self.session.commit()
            return EmployeeDTO.model_validate(employee_db)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                raise DuplicatedException(str(error.orig)) from error
            raise DatabaseException(str(error)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_employee(self, employee_id: UUID) -> None:
        try:
            statement = (
                update(Employee)
                .where(Employee.id.__eq__(employee_id))
                .values(is_deleted=True)
            )
            await self.session.execute(statement)
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def list_employee(self) -> List[EmployeeDTO]:
        try:
            statement = select(Employee).where(Employee.is_deleted.is_(False))
            result = await self.session.execute(statement)
            employees_db = result.scalars().all()
            return [EmployeeDTO.model_validate(row) for row in employees_db]
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
