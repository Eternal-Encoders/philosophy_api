from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Models import GameProgressDB
from Schemas.game_progress import SGameProgressCreate, SGameProgressUpdate


class GameProgressRepository(GenericRepository[
                                 GameProgressDB,
                                 SGameProgressCreate,
                                 SGameProgressUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(GameProgressDB, session)


async def get_game_progress_rep(
    session: AsyncSession = Depends(get_session)
):
    return GameProgressRepository(session)
