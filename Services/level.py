import uuid
from fastapi import HTTPException, Depends
from Infrastructure.Repositories.level import LevelRepository, get_level_rep
from Infrastructure.Repositories.level_ending import (LevelEndingRepository,
                                                      get_level_ending_rep)
from Schemas.level import SLevelCreate, SLevel
from Schemas.level_ending import SLevelEndingCreate


class LevelService:
    def __init__(
            self,
            level_rep: LevelRepository,
            level_ending_rep: LevelEndingRepository,
    ):
        self.level_rep = level_rep
        self.level_ending_rep = level_ending_rep

    async def create_level(
            self,
            level: SLevelCreate
    ):
        level_db = await self.level_rep.create(level)

        new_ending = SLevelEndingCreate(
            level_id=level_db.id,
            name="Default Ending",
            is_default=True
        )
        ending_db = await self.level_ending_rep.create(
            new_ending
        )
        if not ending_db:
            raise HTTPException(status_code=400,
                                detail="Level ending was not created")

        if level_db:
            return SLevel.model_validate(level_db)
        else:
            raise HTTPException(status_code=400,
                                detail="Level was not created")

    async def get_level_by_id(
            self,
            level_id: uuid.UUID
    ):
        level_db = await self.level_rep.get_by_id(level_id)
        if level_db:
            return SLevel.model_validate(level_db)
        else:
            raise HTTPException(status_code=404,
                                detail="Level not found")

    async def get_all_levels(self):
        levels_db = await self.level_rep.get_all()
        return [SLevel.model_validate(level_db)
                for level_db in levels_db]

    async def delete_level(self, level_id: uuid.UUID):
        if not await self.level_rep.delete(level_id):
            raise HTTPException(status_code=404,
                                detail="Level not found")


async def get_level_service(
    level_rep: LevelRepository = Depends(get_level_rep),
    level_ending_rep: LevelEndingRepository = Depends(get_level_ending_rep)
):
    return LevelService(level_rep,
                        level_ending_rep)
