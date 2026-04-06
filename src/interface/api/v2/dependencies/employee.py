from typing import Annotated

from fastapi import Depends

from src.domain.service.employee import EmployeeService
from src.domain.use_case.employee import EmployeeUseCase
from src.infrastructure.repositories.employee_postgres import EmployeeRepositoryPostgres
from src.interface.api.v2.controller.employee import EmployeeController
from src.interface.api.v2.dependencies.common.session import VerifiedSessionDep


async def get_employee_controller(
    session: VerifiedSessionDep,
) -> EmployeeController:
    """
    Singleton para o controller de companias.
    """
    employee_repository = EmployeeRepositoryPostgres(session)
    employee_service = EmployeeService(employee_repository)
    employee_use_case = EmployeeUseCase(employee_service)
    return EmployeeController(employee_use_case)


EmployeeRepositoryDep = Annotated[EmployeeController, Depends(get_employee_controller)]
