from typing import Annotated

from fastapi import Depends

from src.domain.service.loan_operation import LoanOperationService
from src.domain.use_case.loan_operation import LoanOperationUseCase
from src.infrastructure.repositories.loan_operation_postgres import (
    LoanOperationPostgresRepository,
)
from src.interface.api.v2.controller.loan_operation import LoanOperationController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_loan_operation_controller(
    session: VerifiedSessionDep,
) -> LoanOperationController:
    repository = LoanOperationPostgresRepository(session)
    service = LoanOperationService(repository)
    use_case = LoanOperationUseCase(service)
    return LoanOperationController(use_case)


LoanOperationControllerDep = Annotated[
    LoanOperationController, Depends(get_loan_operation_controller)
]
