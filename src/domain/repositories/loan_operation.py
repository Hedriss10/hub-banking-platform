from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationOutDTO,
    LoanOperationUpdateDTO,
)


class LoanOperationRepository(ABC):
    @abstractmethod
    async def list_loan_operations(self) -> List[LoanOperationOutDTO]: ...

    @abstractmethod
    async def create_loan_operation(
        self, loan_operation: LoanOperationCreateDTO
    ) -> LoanOperationOutDTO: ...

    @abstractmethod
    async def get_loan_operation_by_id(
        self, id: UUID
    ) -> Optional[LoanOperationOutDTO]: ...

    @abstractmethod
    async def update_loan_operation(
        self,
        loan_operation_id: UUID,
        loan_operation: LoanOperationUpdateDTO,
    ) -> Optional[LoanOperationOutDTO]: ...

    @abstractmethod
    async def delete_loan_operation(self, loan_operation_id: UUID) -> None: ...
