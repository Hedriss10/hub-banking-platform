from typing import Annotated

from fastapi import Depends

from src.domain.service.proposal import ProposalService
from src.domain.use_case.proposal import ProposalUseCase
from src.infrastructure.repositories.proposal_postgres import ProposalPostgresRepository
from src.interface.api.v2.controller.proposal import ProposalController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_proposal_controller(
    session: VerifiedSessionDep,
) -> ProposalController:
    repository = ProposalPostgresRepository(session)
    service = ProposalService(repository)
    use_case = ProposalUseCase(service)
    return ProposalController(use_case)


ProposalControllerDep = Annotated[ProposalController, Depends(get_proposal_controller)]
