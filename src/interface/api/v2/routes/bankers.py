from typing import List
from uuid import UUID

from fastapi import APIRouter, Response, status

from src.interface.api.v2.dependencies.bankers import BankersRepositoryDep
from src.interface.api.v2.dependencies.common.auth_employee import CurrentEmployeeIdDep
from src.interface.api.v2.schemas.bankers import (
    BankerCreateSchema,
    BankerOutSchema,
    BankerUpdateSchema,
)

tags_metadata = {
    'name': 'Bankers',
    'description': ('Modulo de bankers.'),
}


router = APIRouter(
    prefix='/bankers',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=BankerOutSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Criar um novo banco',
    description='Cria um novo banco (regista quem criou via token JWT).',
)
async def create_banker(
    banker: BankerCreateSchema,
    controller: BankersRepositoryDep,
    _employee_id: CurrentEmployeeIdDep,
) -> BankerOutSchema:
    return await controller.create_banker(banker, _employee_id)


@router.get(
    '',
    response_model=List[BankerOutSchema],
    status_code=status.HTTP_200_OK,
    summary='Listar bancos',
    description='Lista bancos ativos',
)
async def list_bankers(
    controller: BankersRepositoryDep,
) -> List[BankerOutSchema]:
    return await controller.list_bankers()


@router.get(
    '/{banker_id}',
    response_model=BankerOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Obter banco',
    description='Obtém um banco por id.',
)
async def get_banker(
    banker_id: UUID,
    controller: BankersRepositoryDep,
) -> BankerOutSchema:
    return await controller.get_banker(banker_id)


@router.patch(
    '/{banker_id}',
    response_model=BankerOutSchema,
    status_code=status.HTTP_200_OK,
    summary='Atualizar banco',
    description='Atualiza o nome do banco.',
)
async def update_banker(
    banker_id: UUID,
    banker: BankerUpdateSchema,
    controller: BankersRepositoryDep,
    _employee_id: CurrentEmployeeIdDep,
) -> BankerOutSchema:
    return await controller.update_banker(banker_id, banker)


@router.delete(
    '/{banker_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Excluir banco',
    description='Exclusão lógica.',
)
async def delete_banker(
    banker_id: UUID,
    controller: BankersRepositoryDep,
    _employee_id: CurrentEmployeeIdDep,
) -> Response:
    await controller.delete_banker(banker_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
