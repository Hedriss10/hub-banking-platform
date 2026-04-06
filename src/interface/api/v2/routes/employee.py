from typing import List
from uuid import UUID

from fastapi import APIRouter, Response, status

from src.interface.api.v2.dependencies.employee import EmployeeRepositoryDep
from src.interface.api.v2.schemas.employee import (
    EmployeeCreateSchema,
    EmployeeSchema,
    EmployeeUpdateSchema,
)

tags_metadata = {
    'name': 'Funcionários',
    'description': ('Modulo de funcionários.'),
}


router = APIRouter(
    prefix='/employees',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=EmployeeSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Cria um novo funcionário',
    description='Cria um novo funcionário',
)
async def create_employee(
    employee: EmployeeCreateSchema,
    controller: EmployeeRepositoryDep,
) -> EmployeeSchema:
    return await controller.create_employee(employee)


@router.get(
    '',
    response_model=List[EmployeeSchema],
    status_code=status.HTTP_200_OK,
    summary='Lista todos os funcionários',
    description='Lista todos os funcionários',
)
async def list_employees(
    controller: EmployeeRepositoryDep,
) -> List[EmployeeSchema]:
    return await controller.list_employee()


@router.get(
    '/{employee_id}',
    response_model=EmployeeSchema,
    status_code=status.HTTP_200_OK,
    summary='Obtém um funcionário',
    description='Obtém um funcionário',
)
async def get_employee(
    employee_id: UUID,
    controller: EmployeeRepositoryDep,
) -> EmployeeSchema:
    return await controller.get_employee(employee_id)


@router.patch(
    '/{employee_id}',
    response_model=EmployeeSchema,
    status_code=status.HTTP_200_OK,
    summary='Atualiza um funcionário',
    description='Atualiza um funcionário',
)
async def update_employee(
    employee_id: UUID,
    employee: EmployeeUpdateSchema,
    controller: EmployeeRepositoryDep,
) -> EmployeeSchema:
    return await controller.update_employee(employee_id, employee)


@router.delete(
    '/{employee_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta um funcionário',
    description='Deleta um funcionário',
)
async def delete_employee(
    employee_id: UUID,
    controller: EmployeeRepositoryDep,
) -> None:
    await controller.delete_employee(employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
