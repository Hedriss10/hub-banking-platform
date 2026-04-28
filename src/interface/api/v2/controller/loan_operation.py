from typing import List
from uuid import UUID

from src.domain.dtos.loan_operation import (
    LoanOperationCreateDTO,
    LoanOperationOutDTO,
    LoanOperationUpdateDTO,
)
from src.domain.use_case.loan_operation import LoanOperationUseCase
from src.interface.api.v2.schemas.loan_operation import (
    LoanOperationCreateSchema,
    LoanOperationOutSchema,
    LoanOperationUpdateSchema,
)


def _loan_operation_out_to_schema(dto: LoanOperationOutDTO) -> LoanOperationOutSchema:
    return LoanOperationOutSchema(
        id=dto.id,
        name=dto.name,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        is_deleted=dto.is_deleted,
        created_by=dto.created_by,
    )


class LoanOperationController:
    def __init__(self, loan_operation_use_case: LoanOperationUseCase):
        self.loan_operation_use_case = loan_operation_use_case

    async def list_loan_operations(self) -> List[LoanOperationOutSchema]:
        items = await self.loan_operation_use_case.list_loan_operations()
        return [_loan_operation_out_to_schema(row) for row in items]

    async def get_loan_operation(
        self, loan_operation_id: UUID
    ) -> LoanOperationOutSchema:
        dto = await self.loan_operation_use_case.get_loan_operation(loan_operation_id)
        return _loan_operation_out_to_schema(dto)

    async def create_loan_operation(
        self,
        loan_operation: LoanOperationCreateSchema,
        created_by: UUID,
    ) -> LoanOperationOutSchema:
        dto = LoanOperationCreateDTO(
            name=loan_operation.name,
            created_by=created_by,
        )
        out = await self.loan_operation_use_case.create_loan_operation(dto)
        return _loan_operation_out_to_schema(out)

    async def update_loan_operation(
        self,
        loan_operation_id: UUID,
        loan_operation: LoanOperationUpdateSchema,
    ) -> LoanOperationOutSchema:
        update_dto = LoanOperationUpdateDTO.model_validate(loan_operation.model_dump())
        out = await self.loan_operation_use_case.update_loan_operation(
            loan_operation_id, update_dto
        )
        return _loan_operation_out_to_schema(out)

    async def delete_loan_operation(self, loan_operation_id: UUID) -> None:
        await self.loan_operation_use_case.delete_loan_operation(loan_operation_id)
