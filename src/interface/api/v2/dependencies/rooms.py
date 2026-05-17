from typing import Annotated

from fastapi import Depends

from src.domain.service.rooms import RoomsService
from src.domain.use_case.rooms import RoomsUseCase
from src.infrastructure.repositories.rooms_postgres import RoomsPostgresRepository
from src.interface.api.v2.controller.rooms import RoomsController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_rooms_controller(
    session: VerifiedSessionDep,
) -> RoomsController:
    repository = RoomsPostgresRepository(session)
    service = RoomsService(repository)
    use_case = RoomsUseCase(service)
    return RoomsController(use_case)


RoomsControllerDep = Annotated[RoomsController, Depends(get_rooms_controller)]
