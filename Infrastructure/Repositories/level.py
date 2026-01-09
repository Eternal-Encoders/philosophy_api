from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Models.level import LevelDB
from Schemas.level import SLevelCreate, SLevelUpdate


class LevelRepository(GenericRepository[LevelDB, SLevelCreate, SLevelUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(LevelDB, session)


async def get_level_rep(
    session: AsyncSession = Depends(get_session)
):
    return LevelRepository(session)
