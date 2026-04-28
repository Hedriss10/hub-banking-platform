from typing import List
from uuid import UUID

from fastapi import APIRouter, Response, status

from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.dependencies.financial_agreements import (
    FinancialAgreementsControllerDep,
)
from src.interface.api.v2.schemas.financial_agreements import (
    FinancialAgreementsCreateSchema,
    FinancialAgreementsOutSchema,
    FinancialAgreementsUpdateSchema,
)

tags_metadata = {
    'name': 'Financial agreements',
    'description': 'Financial agreements module.',
}


router = APIRouter(
    prefix='/financial-agreements',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=FinancialAgreementsOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Create financial agreement',
    description='Creates a financial agreement (creator is taken from the JWT).',
)
async def create_financial_agreement(
    financial_agreement: FinancialAgreementsCreateSchema,
    controller: FinancialAgreementsControllerDep,
    _employee_id: CurrentEmployeeIdDep,
) -> FinancialAgreementsOutSchema:
    return await controller.create_financial_agreement(
        financial_agreement, _employee_id
    )


@router.get(
    '/banks/{bank_id}',
    response_model=List[FinancialAgreementsOutSchema],
    status_code=status.HTTP_200_OK,
    summary='List financial agreements by bank',
    description='Lists non-deleted financial agreements for the given bank id.',
)
async def list_financial_agreements(
    bank_id: UUID,
    controller: FinancialAgreementsControllerDep,
) -> List[FinancialAgreementsOutSchema]:
    return await controller.list_financial_agreements(bank_id)


@router.get(
    '/{financial_agreement_id}',
    response_model=FinancialAgreementsOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Get financial agreement',
    description='Returns a financial agreement by id.',
)
async def get_financial_agreement(
    financial_agreement_id: UUID,
    controller: FinancialAgreementsControllerDep,
) -> FinancialAgreementsOutSchema:
    return await controller.get_financial_agreement(financial_agreement_id)


@router.patch(
    '/{financial_agreement_id}',
    response_model=FinancialAgreementsOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Update financial agreement',
    description='Updates a financial agreement.',
)
async def update_financial_agreement(
    financial_agreement_id: UUID,
    financial_agreement: FinancialAgreementsUpdateSchema,
    controller: FinancialAgreementsControllerDep,
) -> FinancialAgreementsOutSchema:
    return await controller.update_financial_agreement(
        financial_agreement_id, financial_agreement
    )


@router.delete(
    '/{financial_agreement_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete financial agreement',
    description='Soft-deletes a financial agreement.',
)
async def delete_financial_agreement(
    financial_agreement_id: UUID,
    controller: FinancialAgreementsControllerDep,
) -> Response:
    await controller.delete_financial_agreement(financial_agreement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
