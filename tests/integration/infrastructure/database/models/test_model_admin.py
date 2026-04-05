import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models.admin import Admin
from src.infrastructure.database.models.common.role import RoleStatus

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope='session'),
]


async def test_admin_model_can_be_created(
    async_session: AsyncSession, unique_admin_email: str
):
    admin = Admin(
        email=unique_admin_email,
        password='password',
        role=RoleStatus.ADMIN,
    )
    async_session.add(admin)
    await async_session.commit()
    assert admin.id is not None


async def test_admin_model_can_be_retrieved(
    async_session: AsyncSession, unique_admin_email: str
):
    admin = Admin(
        email=unique_admin_email,
        password='password',
        role=RoleStatus.ADMIN,
    )
    async_session.add(admin)
    await async_session.commit()
    retrieved_admin = await async_session.get(Admin, admin.id)
    assert retrieved_admin is not None


async def test_admin_model_can_be_updated(
    async_session: AsyncSession, unique_admin_email: str
):
    admin = Admin(
        email=unique_admin_email,
        password='password',
        role=RoleStatus.ADMIN,
    )
    async_session.add(admin)
    await async_session.commit()
    new_email = f'jane.{uuid.uuid4().hex}@example.com'
    admin.email = new_email
    await async_session.commit()
    updated_admin = await async_session.get(Admin, admin.id)
    assert updated_admin is not None
    assert updated_admin.email == new_email


async def test_admin_model_can_be_listed(
    async_session: AsyncSession, unique_admin_email: str
):
    admins = [
        Admin(
            email=unique_admin_email,
            password='password',
            role=RoleStatus.ADMIN,
        ),
    ]
    async_session.add_all(admins)
    await async_session.commit()
    listed_admins = await async_session.execute(
        select(Admin).where(Admin.email == unique_admin_email)
    )
    assert len(listed_admins.scalars().all()) == len(admins)


async def test_admin_model_can_be_filtered(
    async_session: AsyncSession, unique_admin_email: str
):
    admins = [
        Admin(
            email=unique_admin_email,
            password='password',
            role=RoleStatus.ADMIN,
        ),
    ]
    async_session.add_all(admins)
    await async_session.commit()
    filtered_admins = await async_session.execute(
        select(Admin).where(Admin.email == unique_admin_email)
    )
    rows = filtered_admins.scalars().all()
    assert len(rows) == 1
    assert rows[0].email == unique_admin_email
