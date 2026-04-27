import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.bankers import BankerCreateDto, BankerOutDto, BankerUpdateDto
from src.domain.exceptions.bankers import BankerNameAlreadyExistsException
from src.domain.repositories.bankers import BankersRepository
from src.infrastructure.database.models.bankers import BankersModel
from src.infrastructure.database.utils.status_code import is_unique_violation

# PostgreSQL detail típico: Key (name)=(valor)
_BANKERS_NAME_UNIQUE_DETAIL = re.compile(
    r'Key\s*\(\s*name\s*\)\s*=\s*\(\s*(.*?)\s*\)',
    re.IGNORECASE | re.DOTALL,
)


def _raise_duplicate_banker_name_or_generic(error: IntegrityError) -> None:
    raw = str(getattr(error, 'orig', None) or error)
    if 'bankers_name_key' not in raw:
        raise DuplicatedException(raw) from error
    match = _BANKERS_NAME_UNIQUE_DETAIL.search(raw)
    dup_name = match.group(1).strip() if match else None
    raise BankerNameAlreadyExistsException(name=dup_name or None) from error


class BankersPostgresRepository(BankersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_bankers(self) -> List[BankerOutDto]:
        try:
            statement = (
                select(BankersModel)
                .where(BankersModel.is_deleted.is_(False))
                .order_by(BankersModel.name)
            )
            result = await self.session.execute(statement)
            rows = result.scalars().all()
            return [BankerOutDto.model_validate(row) for row in rows]
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_banker(self, banker_id: UUID) -> Optional[BankerOutDto]:
        try:
            result = await self.session.execute(
                select(BankersModel).where(
                    BankersModel.id.__eq__(banker_id),
                    BankersModel.is_deleted.__eq__(False),
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return BankerOutDto.model_validate(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def create_banker(self, banker: BankerCreateDto) -> BankerOutDto:
        new_banker = BankersModel(**banker.model_dump())
        try:
            self.session.add(new_banker)
            await self.session.commit()
            await self.session.refresh(new_banker)
            return BankerOutDto.model_validate(new_banker)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                _raise_duplicate_banker_name_or_generic(error)
            raise DatabaseException(str(error.orig)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_banker(
        self, banker_id: UUID, banker: BankerUpdateDto
    ) -> Optional[BankerOutDto]:
        update_data = banker.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_banker(banker_id)
        try:
            stmt = (
                update(BankersModel)
                .where(
                    BankersModel.id.__eq__(banker_id),
                    BankersModel.is_deleted.is_(False),
                )
                .values(**update_data)
                .returning(BankersModel)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return BankerOutDto.model_validate(row)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                _raise_duplicate_banker_name_or_generic(error)
            raise DatabaseException(str(error.orig)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_banker(self, banker_id: UUID) -> None:
        try:
            statement = (
                update(BankersModel)
                .where(
                    BankersModel.id.__eq__(banker_id),
                    BankersModel.is_deleted.is_(False),
                )
                .values(is_deleted=True)
            )
            await self.session.execute(statement)
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
