import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.admin import Admin
from src.infrastructure.database.models.common.role import RoleStatus
from src.infrastructure.database.models.employee import Employee
from src.infrastructure.database.session import get_session_factory
from src.infrastructure.utils.get_argon import hash_password

DEV_USER_EMAIL = 'usuario.dev@hotmail.com'
DEV_USER_PASSWORD = 'Binfae@45'
DEV_USER_FIRST_NAME = 'Usuario'
DEV_USER_LAST_NAME = 'Dev'
DEV_USER_DOCUMENT = '99999999999'


async def _ensure_dev_employee(session: AsyncSession, password_hash: str) -> bool:
    existing = await session.scalar(
        select(Employee).where(Employee.email == DEV_USER_EMAIL),
    )
    if existing is not None:
        return False

    session.add(
        Employee(
            first_name=DEV_USER_FIRST_NAME,
            last_name=DEV_USER_LAST_NAME,
            role=RoleStatus.ADMIN,
            document=DEV_USER_DOCUMENT,
            email=DEV_USER_EMAIL,
            password=password_hash,
        ),
    )
    return True


async def _ensure_dev_admin(session: AsyncSession, password_hash: str) -> bool:
    existing = await session.scalar(
        select(Admin).where(Admin.email == DEV_USER_EMAIL),
    )
    if existing is not None:
        return False

    session.add(
        Admin(
            email=DEV_USER_EMAIL,
            password=password_hash,
            role=RoleStatus.ADMIN,
        ),
    )
    return True


async def init_system(session: AsyncSession) -> None:
    """Cria usuário dev em `employees` e `admins`, se ainda não existirem."""
    password_hash = hash_password(DEV_USER_PASSWORD)
    created = await _ensure_dev_employee(session, password_hash)
    created = await _ensure_dev_admin(session, password_hash) or created

    if created:
        await session.commit()


async def run_init_system() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        await init_system(session)


def main() -> None:
    asyncio.run(run_init_system())
