from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.employee import EmployeeDTO
from src.domain.repositories.auth import AuthRepository
from src.infrastructure.database.models.employee import Employee


class AuthPostgresRepository(AuthRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_employee_by_email(self, email: str) -> Optional[EmployeeDTO]:
        """
        Carrega o funcionário;
        validação de senha em `AuthService.verify_password`.
        """
        try:
            statement = select(Employee).where(
                Employee.email.__eq__(email),
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
