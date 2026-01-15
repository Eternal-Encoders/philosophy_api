from fastapi import Depends
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Schemas.game_progress import SGameProgressCreate, SGameProgressUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from Models import GameProgressDB


class GameProgressRepository(GenericRepository[
                                 GameProgressDB,
                                 SGameProgressCreate,
                                 SGameProgressUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(GameProgressDB, session)


async def get_game_progress_rep(
    session: AsyncSession | None = None
):
    if session is None:
        session = Depends(get_session)
    assert session is not None

    return GameProgressRepository(session)
