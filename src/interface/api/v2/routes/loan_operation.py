from typing import List
from uuid import UUID

from fastapi import APIRouter, Response, status

from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.loan_operation import LoanOperationControllerDep
from src.interface.api.v2.schemas.loan_operation import (
    LoanOperationCreateSchema,
    LoanOperationOutSchema,
    LoanOperationUpdateSchema,
)

tags_metadata = {
    'name': 'Loan operations',
    'description': 'Loan operations module.',
}

router = APIRouter(
    prefix='/loan-operations',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=LoanOperationOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create loan operation',
    description='Creates a loan operation',
)
async def create_loan_operation(
    loan_operation: LoanOperationCreateSchema,
    controller: LoanOperationControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> LoanOperationOutSchema:
    return await controller.create_loan_operation(loan_operation, _employee_id)


@router.get(
    '',
    response_model=List[LoanOperationOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List loan operations',
    description='Lists non-deleted loan operations.',
)
async def list_loan_operations(
    controller: LoanOperationControllerDep,
) -> List[LoanOperationOutSchema]:
    return await controller.list_loan_operations()


@router.get(
    '/{loan_operation_id}',
    response_model=LoanOperationOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Get loan operation',
    description='Returns a loan operation by id.',
)
async def get_loan_operation(
    loan_operation_id: UUID,
    controller: LoanOperationControllerDep,
) -> LoanOperationOutSchema:
    return await controller.get_loan_operation(loan_operation_id)


@router.patch(
    '/{loan_operation_id}',
    response_model=LoanOperationOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Update loan operation',
    description='Updates a loan operation.',
)
async def update_loan_operation(
    loan_operation_id: UUID,
    loan_operation: LoanOperationUpdateSchema,
    controller: LoanOperationControllerDep,
) -> LoanOperationOutSchema:
    return await controller.update_loan_operation(loan_operation_id, loan_operation)


@router.delete(
    '/{loan_operation_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete loan operation',
    description='Soft-deletes a loan operation.',
)
async def delete_loan_operation(
    loan_operation_id: UUID,
    controller: LoanOperationControllerDep,
) -> Response:
    await controller.delete_loan_operation(loan_operation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
