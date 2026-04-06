from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.employee import EmployeeCreateDTO, EmployeeDTO, EmployeeUpdateDTO


class EmployeeRepository(ABC):
    @abstractmethod
    async def create_employee(self, employee: EmployeeCreateDTO) -> EmployeeDTO: ...

    @abstractmethod
    async def get_employee_by_id(self, employee_id: UUID) -> Optional[EmployeeDTO]: ...

    @abstractmethod
    async def update_employee(
        self, employee_id: UUID, employee: EmployeeUpdateDTO
    ) -> EmployeeDTO: ...

    @abstractmethod
    async def delete_employee(self, employee_id: UUID) -> None: ...

    @abstractmethod
    async def list_employee(self) -> List[EmployeeDTO]: ...
