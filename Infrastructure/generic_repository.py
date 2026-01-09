import uuid
from collections.abc import Callable
from typing import TypeVar, Generic, Type, Optional
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from Exceptions.handler import handle_fk

T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class GenericRepository(Generic[T, CreateSchema, UpdateSchema]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, model_id: uuid.UUID) -> Optional[T]:
        async with self.session as session:
            result = await session.execute(
                select(self.model).where(model_id == self.model.id)
            )
            return result.scalar_one_or_none()

    async def get_all(self):
        async with self.session as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()

    async def count(self, predicate: Optional[Callable] = None):
        async with self.session as session:
            query = select(func.count()).select_from(self.model)
            if predicate:
                if callable(predicate):
                    query = query.where(predicate)
            result = await session.execute(query)
            return result.scalar_one()

    async def create(self, obj_in: CreateSchema) -> Optional[T]:
        async with self.session as session:
            try:
                obj_data = obj_in.model_dump()
                db_obj = self.model(**obj_data)
                session.add(db_obj)
                await session.flush()
                await session.commit()
                return db_obj

            except IntegrityError as e:
                await handle_fk(e, session)

    async def update(self, obj_in: UpdateSchema, model_id: uuid.UUID):
        async with self.session as session:
            try:
                obj = await self.get_by_id(model_id)
                data = obj_in.model_dump()
                if obj:
                    for key, value in data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                    session.add(obj)
                    await session.commit()
                    await session.refresh(obj)
                    return obj

            except IntegrityError as e:
                await handle_fk(e, session)

    async def delete(self, model_id: uuid.UUID) -> bool:
        async with self.session as session:
            obj = await self.get_by_id(model_id)
            if obj:
                await session.delete(obj)
                await session.commit()
                return True
            return False
