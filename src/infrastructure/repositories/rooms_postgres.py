from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException, DuplicatedException
from src.domain.dtos.rooms import RoomCreateDTO, RoomDTO, RoomUpdateDTO
from src.domain.dtos.rooms_employee import (
    RoomEmployeeCreateDTO,
    RoomEmployeeDTO,
    RoomEmployeeListDTO,
)
from src.domain.repositories.rooms import RoomRepository
from src.infrastructure.database.models.employee import Employee
from src.infrastructure.database.models.rooms import RoomsModel
from src.infrastructure.database.models.rooms_employee import RoomsEmployee
from src.infrastructure.database.utils.status_code import is_unique_violation


class RoomsPostgresRepository(RoomRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_room_by_id(self, room_id: UUID) -> Optional[RoomDTO]:
        try:
            stmt = (
                select(RoomsModel)
                .where(RoomsModel.id.__eq__(room_id))
                .where(RoomsModel.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return RoomDTO.model_validate(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_all_rooms(self) -> List[RoomDTO]:
        try:
            stmt = select(RoomsModel).where(RoomsModel.is_deleted.is_(False))
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            return [RoomDTO.model_validate(row) for row in rows]
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def create_room(self, room: RoomCreateDTO) -> RoomDTO:
        try:
            row = RoomsModel(
                name=room.name,
                created_by=room.created_by,
            )
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return RoomDTO.model_validate(row)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                raise DuplicatedException(str(error.orig)) from error
            raise DatabaseException(str(error)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def update_room(
        self, room_id: UUID, room: RoomUpdateDTO
    ) -> Optional[RoomDTO]:
        payload = room.model_dump(exclude_unset=True, exclude_none=True)
        if not payload:
            return await self.get_room_by_id(room_id)
        try:
            stmt = (
                update(RoomsModel)
                .where(RoomsModel.id.__eq__(room_id))
                .where(RoomsModel.is_deleted.is_(False))
                .values(**payload)
                .returning(RoomsModel)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                await self.session.rollback()
                return None
            await self.session.commit()
            return RoomDTO.model_validate(row)
        except IntegrityError as error:
            await self.session.rollback()
            if is_unique_violation(error):
                raise DuplicatedException(str(error.orig)) from error
            raise DatabaseException(str(error)) from error
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_room(self, room_id: UUID) -> None:
        try:
            stmt = (
                update(RoomsModel)
                .where(RoomsModel.id.__eq__(room_id))
                .where(RoomsModel.is_deleted.is_(False))
                .values(is_deleted=True)
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                await self.session.rollback()
                return
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def create_room_employee(
        self, room_employee: RoomEmployeeCreateDTO
    ) -> RoomEmployeeDTO:
        try:
            row = RoomsEmployee(
                room_id=room_employee.room_id,
                employee_id=room_employee.employee_id,
            )
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return RoomEmployeeDTO.model_validate(row)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def get_room_employees(self, room_id: UUID) -> List[RoomEmployeeListDTO]:
        try:
            stmt = (
                select(
                    RoomsEmployee,
                    Employee.first_name,
                    Employee.last_name,
                )
                .join(Employee, Employee.id.__eq__(RoomsEmployee.employee_id))
                .where(RoomsEmployee.room_id.__eq__(room_id))
                .where(RoomsEmployee.is_deleted.is_(False))
                .where(Employee.is_deleted.is_(False))
            )
            result = await self.session.execute(stmt)
            rows = result.all()
            return [
                RoomEmployeeListDTO(
                    id=rooms_employee.id,
                    room_id=rooms_employee.room_id,
                    employee_id=rooms_employee.employee_id,
                    first_name=first_name,
                    last_name=last_name,
                )
                for rooms_employee, first_name, last_name in rows
            ]
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error

    async def delete_room_employee(self, room_id: UUID, employee_id: UUID) -> None:
        try:
            stmt = (
                update(RoomsEmployee)
                .where(RoomsEmployee.room_id.__eq__(room_id))
                .where(RoomsEmployee.employee_id.__eq__(employee_id))
                .where(RoomsEmployee.is_deleted.is_(False))
                .values(is_deleted=True)
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                await self.session.rollback()
                return
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise DatabaseException(str(error)) from error
