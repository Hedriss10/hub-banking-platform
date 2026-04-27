from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models.bankers import BankersModel

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]

RESULT_LIST_BANKERS = 2


async def test_bankers_model_can_be_created(
    async_session: AsyncSession,
    unique_banker_name: str,
    created_by_employee_id: UUID,
) -> None:
    banker = BankersModel(
        name=unique_banker_name,
        created_by=created_by_employee_id,
    )
    async_session.add(banker)
    await async_session.commit()
    assert banker.id is not None
    retrieved_banker = await async_session.get(BankersModel, banker.id)
    assert retrieved_banker is not None
    assert retrieved_banker.name == unique_banker_name
    assert retrieved_banker.created_by == created_by_employee_id


async def test_bankers_model_can_be_retrieved(
    async_session: AsyncSession,
    unique_banker_name: str,
    created_by_employee_id: UUID,
) -> None:
    banker = BankersModel(
        name=unique_banker_name,
        created_by=created_by_employee_id,
    )
    async_session.add(banker)
    await async_session.commit()
    retrieved_banker = await async_session.get(BankersModel, banker.id)
    assert retrieved_banker is not None
    assert retrieved_banker.name == unique_banker_name


async def test_list_bankers(
    async_session: AsyncSession,
    unique_banker_name: str,
    other_unique_banker_name: str,
    created_by_employee_id: UUID,
) -> None:
    assert unique_banker_name != other_unique_banker_name
    bankers = [
        BankersModel(name=unique_banker_name, created_by=created_by_employee_id),
        BankersModel(name=other_unique_banker_name, created_by=created_by_employee_id),
    ]
    async_session.add_all(bankers)
    await async_session.commit()

    result = await async_session.execute(
        select(BankersModel).where(
            BankersModel.name.in_((unique_banker_name, other_unique_banker_name))
        )
    )
    rows = list(result.scalars().all())
    assert len(rows) == RESULT_LIST_BANKERS
    assert {r.name for r in rows} == {unique_banker_name, other_unique_banker_name}
