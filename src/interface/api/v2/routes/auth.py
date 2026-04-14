from fastapi import APIRouter, status

from src.interface.api.v2.dependencies.auth import AuthRepositoryDep
from src.interface.api.v2.schemas.auth import LoginRequestSchema, LoginResponseSchema

tags_metadata = {
    'name': 'Login',
    'description': ('Modulo de login.'),
}


router = APIRouter(
    prefix='/login',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary='Login',
    description='Login',
)
async def login(
    login: LoginRequestSchema,
    controller: AuthRepositoryDep,
) -> LoginResponseSchema:
    return await controller.login(login)
