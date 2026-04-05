from typing import List, Optional
from uuid import UUID

from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO
from src.domain.repositories.employee import EmployeeRepository


class EmployeeService:
    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    async def create_employee(self, employee: EmployeeCreateDTO) -> EmployeeDTO:
        return await self.employee_repository.create_employee(employee)

    async def get_employee(self, employee_id: UUID) -> Optional[EmployeeDTO]:
        return await self.employee_repository.get_employee_by_id(employee_id)

    async def update_employee(
        self, employee_id: UUID, employee: EmployeeUpdateDTO
    ) -> EmployeeDTO:
        return await self.employee_repository.update_employee(employee_id, employee)

    async def delete_employee(self, employee_id: UUID) -> None:
        return await self.employee_repository.delete_employee(employee_id)

    async def list_employee(self) -> List[EmployeeDTO]:
        return await self.employee_repository.list_employee()
