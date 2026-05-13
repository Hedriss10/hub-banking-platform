from typing import Annotated

from fastapi import Depends

from src.domain.service.safra import SafraService
from src.domain.use_case.safra import SafraUseCase
from src.infrastructure.repositories.safra_external import SafraExternalRepository
from src.interface.api.v2.controller.safra import SafraController


async def get_safra_controller() -> SafraController:
    safra_repository = SafraExternalRepository()
    safra_service = SafraService(safra_repository)
    safra_use_case = SafraUseCase(safra_service)
    return SafraController(safra_use_case)


SafraControllerDep = Annotated[SafraController, Depends(get_safra_controller)]
