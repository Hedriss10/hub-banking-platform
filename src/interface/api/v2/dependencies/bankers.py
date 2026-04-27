from typing import Annotated

from fastapi import Depends

from src.domain.service.bankers import BankersService
from src.domain.use_case.bankers import BankersUseCase
from src.infrastructure.repositories.banker_postgres import BankersPostgresRepository
from src.interface.api.v2.controller.bankers import BankersController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_bankers_controller(
    session: VerifiedSessionDep,
) -> BankersController:
    """
    Singleton for the bankers controller.
    """
    bankers_repository = BankersPostgresRepository(session)
    banker_service = BankersService(bankers_repository)
    banker_use_case = BankersUseCase(banker_service)
    return BankersController(banker_use_case)


BankersRepositoryDep = Annotated[BankersController, Depends(get_bankers_controller)]
