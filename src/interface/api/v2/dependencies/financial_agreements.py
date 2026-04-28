from typing import Annotated

from fastapi import Depends

from src.domain.service.financial_agreements import FinancialAgreementsService
from src.domain.use_case.financial_agreements import FinancialAgreementsUseCase
from src.infrastructure.repositories.financial_agreements_postgres import (
    FinancialAgreementsPostgresRepository,
)
from src.interface.api.v2.controller.financial_agreements import (
    FinancialAgreementsController,
)
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_financial_agreements_controller(
    session: VerifiedSessionDep,
) -> FinancialAgreementsController:
    """Wires repository, service, use case, and controller for each request."""
    financial_agreements_repository = FinancialAgreementsPostgresRepository(session)
    financial_agreements_service = FinancialAgreementsService(
        financial_agreements_repository
    )
    financial_agreements_use_case = FinancialAgreementsUseCase(
        financial_agreements_service
    )
    return FinancialAgreementsController(financial_agreements_use_case)


FinancialAgreementsControllerDep = Annotated[
    FinancialAgreementsController, Depends(get_financial_agreements_controller)
]
