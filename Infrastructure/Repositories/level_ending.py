import uuid
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Models import LevelEndingDB
from Schemas.level_ending import SLevelEndingCreate, SLevelEndingUpdate


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
    session: AsyncSession = Depends(get_session)
):
    return LevelEndingRepository(session)
