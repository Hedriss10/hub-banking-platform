from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models.loan_operation import LoanOperation

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]

RESULT_LIST_LOAN_OPERATION = 2
LOAN_OPERATION_NAME = 'Loan Operation'


async def test_loan_operation_model_can_be_created(
    async_session: AsyncSession,
    created_by_employee_id: UUID,
) -> None:
    loan_operation = LoanOperation(
        name=LOAN_OPERATION_NAME,
        created_by=created_by_employee_id,
    )
    async_session.add(loan_operation)
    await async_session.commit()
    assert loan_operation.id is not None
    retrieved_loan_operation = await async_session.get(LoanOperation, loan_operation.id)
    assert retrieved_loan_operation is not None
    assert retrieved_loan_operation.name == LOAN_OPERATION_NAME
    assert retrieved_loan_operation.created_by == created_by_employee_id


async def test_list_loan_operation(
    list_loan_operation: list[LoanOperation],
    created_by_employee_id: UUID,
) -> None:
    assert len(list_loan_operation) == RESULT_LIST_LOAN_OPERATION
    assert list_loan_operation[0].name == LOAN_OPERATION_NAME
    assert list_loan_operation[0].created_by == created_by_employee_id
