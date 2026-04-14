from typing import Annotated

from fastapi import Depends

from src.domain.service.auth import AuthService
from src.domain.use_case.auth import AuthUseCase
from src.infrastructure.repositories.auth_postgres import AuthPostgresRepository
from src.interface.api.v2.controller.auth import AuthController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_auth_controller(
    session: VerifiedSessionDep,
) -> AuthController:
    auth_repository = AuthPostgresRepository(session)
    auth_service = AuthService(auth_repository)
    auth_use_case = AuthUseCase(auth_service)
    return AuthController(auth_use_case)


AuthRepositoryDep = Annotated[AuthController, Depends(get_auth_controller)]
