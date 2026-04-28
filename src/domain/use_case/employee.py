from typing import List
from uuid import UUID

from src.core.exceptions.custom import DuplicatedException
from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO
from src.domain.exceptions.employee import (
    EmployeeAlreadyExistsException,
    EmployeeNotFoundException,
)
from src.domain.service.employee import EmployeeService


class EmployeeUseCase:
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service

    async def create_employee(self, employee: EmployeeCreateDTO) -> EmployeeDTO:
        try:
            return await self.employee_service.create_employee(employee)
        except DuplicatedException as error:
            raise EmployeeAlreadyExistsException() from error

    async def get_employee(self, employee_id: UUID) -> EmployeeDTO:
        employee = await self.employee_service.get_employee(employee_id)
        if not employee:
            raise EmployeeNotFoundException(
                message=f'Employee with id {employee_id} not found',
            )
        return employee

    async def update_employee(
        self, employee_id: UUID, payload: EmployeeUpdateDTO
    ) -> EmployeeDTO:
        employee_existing = await self.employee_service.get_employee(employee_id)
        if not employee_existing:
            raise EmployeeNotFoundException(
                message=f'Employee with id {employee_id} not found',
            )
        try:
            return await self.employee_service.update_employee(employee_id, payload)
        except DuplicatedException as error:
            raise EmployeeAlreadyExistsException() from error

    async def delete_employee(self, employee_id: UUID) -> None:
        employee_existing = await self.employee_service.get_employee(employee_id)
        if not employee_existing:
            raise EmployeeNotFoundException(
                message=f'Employee with id {employee_id} not found',
            )
        await self.employee_service.delete_employee(employee_id)

    async def list_employee(self) -> List[EmployeeDTO]:
        return await self.employee_service.list_employee()
