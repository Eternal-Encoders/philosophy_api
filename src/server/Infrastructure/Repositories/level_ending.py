import uuid

from fastapi import Depends
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Schemas.level_ending import SLevelEndingCreate, SLevelEndingUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Models import LevelEndingDB


class LevelEndingRepository(
    GenericRepository[
        LevelEndingDB,
        SLevelEndingCreate,
        SLevelEndingUpdate
    ]
):
    def __init__(self, session: AsyncSession):
        super().__init__(LevelEndingDB, session)

    async def get_default_end_by_level(
            self,
            level_id: uuid.UUID,
    ):
        query = select(LevelEndingDB).where(
            LevelEndingDB.level_id == level_id,
            LevelEndingDB.is_default
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


async def get_level_ending_rep(
    session: AsyncSession | None = None
):
    if session is None:
        session = Depends(get_session)
    assert session is not None

    return LevelEndingRepository(session)
