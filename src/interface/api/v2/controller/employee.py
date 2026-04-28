from typing import List
from uuid import UUID

from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO
from src.domain.use_case.employee import EmployeeUseCase
from src.interface.api.v2.schemas.employee import (
    EmployeeCreateSchema,
    EmployeeSchema,
    EmployeeUpdateSchema,
)


def _employee_dto_to_schema(dto: EmployeeDTO) -> EmployeeSchema:
    """Validate via dumped dict (cross-model boundaries)."""
    return EmployeeSchema.model_validate(dto.model_dump())


class EmployeeController:
    def __init__(self, employee_use_case: EmployeeUseCase):
        self.employee_use_case = employee_use_case

    async def create_employee(self, employee: EmployeeCreateSchema) -> EmployeeSchema:
        dto = EmployeeCreateDTO.model_validate(employee.model_dump())
        created = await self.employee_use_case.create_employee(dto)
        return _employee_dto_to_schema(created)

    async def list_employee(self) -> List[EmployeeSchema]:
        employees = await self.employee_use_case.list_employee()
        return [_employee_dto_to_schema(row) for row in employees]

    async def get_employee(self, employee_id: UUID) -> EmployeeSchema:
        employee = await self.employee_use_case.get_employee(employee_id)
        return _employee_dto_to_schema(employee)

    async def update_employee(
        self, employee_id: UUID, employee: EmployeeUpdateSchema
    ) -> EmployeeSchema:
        dto = EmployeeUpdateDTO.model_validate(
            employee.model_dump(exclude_unset=True, exclude_none=True)
        )
        updated = await self.employee_use_case.update_employee(employee_id, dto)
        return _employee_dto_to_schema(updated)

    async def delete_employee(self, employee_id: UUID) -> None:
        await self.employee_use_case.delete_employee(employee_id)
