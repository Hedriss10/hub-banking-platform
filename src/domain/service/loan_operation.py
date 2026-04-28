from typing import List, Optional
from uuid import UUID

from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationOutDTO,
    LoanOperationUpdateDTO,
)
from src.domain.repositories.loan_operation import LoanOperationRepository


class LoanOperationService:
    def __init__(self, repository: LoanOperationRepository):
        self.repository = repository

    async def create_loan_operation(
        self, loan_operation: LoanOperationCreateDTO
    ) -> LoanOperationOutDTO:
        return await self.repository.create_loan_operation(loan_operation)

    async def get_loan_operation_by_id(self, id: UUID) -> Optional[LoanOperationOutDTO]:
        return await self.repository.get_loan_operation_by_id(id)

    async def update_loan_operation(
        self,
        loan_operation_id: UUID,
        loan_operation: LoanOperationUpdateDTO,
    ) -> Optional[LoanOperationOutDTO]:
        return await self.repository.update_loan_operation(
            loan_operation_id, loan_operation
        )

    async def delete_loan_operation(self, loan_operation_id: UUID) -> None:
        return await self.repository.delete_loan_operation(loan_operation_id)

    async def list_loan_operations(self) -> List[LoanOperationOutDTO]:
        return await self.repository.list_loan_operations()
