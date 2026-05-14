from typing import Annotated

from fastapi import Depends

from src.domain.service.safra import SafraService
from src.domain.use_case.safra import SafraUseCase
from src.domain.use_case.safra_batch_search import SafraBatchSearchUseCase
from src.infrastructure.repositories.safra_batch_search_postgres import (
    SafraBatchSearchPostgresRepository,
)
from src.infrastructure.repositories.safra_external import SafraExternalRepository
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_safra_controller(session: VerifiedSessionDep) -> SafraController:
    safra_repository = SafraExternalRepository()
    safra_service = SafraService(safra_repository)
    safra_use_case = SafraUseCase(safra_service)

    batch_search_repository = SafraBatchSearchPostgresRepository(session)
    safra_batch_search_use_case = SafraBatchSearchUseCase(batch_search_repository)

    return SafraController(safra_use_case, safra_batch_search_use_case)


SafraControllerDep = Annotated[SafraController, Depends(get_safra_controller)]
