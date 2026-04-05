"""
Integração: EmployeeRepositoryPostgres com Postgres real (fixtures em cascata).

"""

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]


async def test_repository_create_get_list(
    employee_repository_postgres,
    employee_create_dto,
) -> None:
    repo = employee_repository_postgres
    created = await repo.create_employee(employee_create_dto)
    assert created.id is not None
    assert created.email == employee_create_dto.email

    fetched = await repo.get_employee_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id

    listed = await repo.list_employee()
    ids = {row.id for row in listed}
    assert created.id in ids


async def test_employee_stack_same_session(
    employee_controller,
    employee_use_case,
    employee_service,
    employee_repository_postgres,
) -> None:
    """Garante que as fixtures compõem a mesma árvore de dependências."""
    assert employee_controller.employee_use_case is employee_use_case
    assert employee_use_case.employee_service is employee_service
    assert employee_service.employee_repository is employee_repository_postgres
