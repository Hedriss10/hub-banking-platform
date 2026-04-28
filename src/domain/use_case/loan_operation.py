from typing import List
from uuid import UUID

from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationOutDTO,
    LoanOperationUpdateDTO,
)
from src.domain.exceptions.loan_operation import LoanOperationNotFoundException
from src.domain.service.loan_operation import LoanOperationService


class LoanOperationUseCase:
    def __init__(self, service: LoanOperationService):
        self.service = service

    async def create_loan_operation(
        self, loan_operation: LoanOperationCreateDTO
    ) -> LoanOperationOutDTO:
        return await self.service.create_loan_operation(loan_operation)

    async def get_loan_operation(self, loan_operation_id: UUID) -> LoanOperationOutDTO:
        row = await self.service.get_loan_operation_by_id(loan_operation_id)
        if not row:
            raise LoanOperationNotFoundException(
                message=(f'Loan operation with id {loan_operation_id} not found'),
            )
        return row

    async def update_loan_operation(
        self,
        loan_operation_id: UUID,
        data: LoanOperationUpdateDTO,
    ) -> LoanOperationOutDTO:
        existing = await self.service.get_loan_operation_by_id(loan_operation_id)
        if not existing:
            raise LoanOperationNotFoundException(
                message=(f'Loan operation with id {loan_operation_id} not found'),
            )
        updated = await self.service.update_loan_operation(loan_operation_id, data)
        if not updated:
            raise LoanOperationNotFoundException(
                message=(f'Loan operation with id {loan_operation_id} not found'),
            )
        return updated

    async def list_loan_operations(self) -> List[LoanOperationOutDTO]:
        return await self.service.list_loan_operations()

    async def delete_loan_operation(self, loan_operation_id: UUID) -> None:
        existing = await self.service.get_loan_operation_by_id(loan_operation_id)
        if not existing:
            raise LoanOperationNotFoundException(
                message=(f'Loan operation with id {loan_operation_id} not found'),
            )
        return await self.service.delete_loan_operation(loan_operation_id)
