from fastapi import Depends
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Models.level import LevelDB
from Schemas.level import SLevelCreate, SLevelUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class LevelRepository(GenericRepository[LevelDB, SLevelCreate, SLevelUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(LevelDB, session)


async def get_level_rep(
    session: AsyncSession  | None = None
):
    if session is None:
        session = Depends(get_session)
    assert session is not None

    return LevelRepository(session)
