import uuid

from fastapi import HTTPException, Depends

from Infrastructure.Repositories.card import CardRepository, get_card_rep
from Infrastructure.Repositories.game_progress import (GameProgressRepository,
                                                       get_game_progress_rep)
from Infrastructure.Repositories.level_ending import (LevelEndingRepository,
                                                      get_level_ending_rep)
from Schemas.game_progress import (SGameProgressCreate, SGameProgressCreateDto,
                                   SGameProgress, SGameProgressUpdate)


class GameProgressService:
    def __init__(
            self,
            game_prog_rep: GameProgressRepository,
            card_rep: CardRepository,
            level_end_rep: LevelEndingRepository
    ):
        self.game_prog_rep = game_prog_rep
        self.card_rep = card_rep
        self.level_end_rep = level_end_rep

    async def create_game_progress(
            self,
            game_prog: SGameProgressCreateDto
    ):
        card = await self.card_rep.get_card_by_level_and_number(
            game_prog.level_id, 1
        )
        if not card:
            raise HTTPException(status_code=404,
                                detail="Card not found")
        new_game_progress = SGameProgressCreate(
            level_id=game_prog.level_id,
            card_id=card.id
        )
        result_db = await (
            self.game_prog_rep.create(new_game_progress)
        )
        if result_db:
            return SGameProgress.model_validate(result_db)
        else:
            raise HTTPException(status_code=400,
                                detail="Game progress was not created")

    async def get_game_progress_by_id(
            self,
            game_prog_id: uuid.UUID
    ):
        game_prog = await self.game_prog_rep.get_by_id(game_prog_id)
        if game_prog:
            return SGameProgress.model_validate(game_prog)
        else:
            raise HTTPException(status_code=404,
                                detail="Game progress not found")

    async def get_all_game_progresses(self):
        game_progs = await self.game_prog_rep.get_all()
        return [SGameProgress.model_validate(game_prog)
                for game_prog in game_progs]

    async def delete_game_progress(self,
                                   game_prog_id: uuid.UUID):
        if not await self.game_prog_rep.delete(game_prog_id):
            raise HTTPException(status_code=404,
                                detail="Game progress not found")

    async def make_move(
            self,
            game_prog_id: uuid.UUID,
            choice: int
    ):
        game_prog = await self.get_game_progress_by_id(game_prog_id)
        if not game_prog:
            raise HTTPException(status_code=404,
                                detail="Game progress not found")
        if game_prog.game_ended:
            raise HTTPException(status_code=400,
                                detail="Game already ended")

        card = await self.card_rep.get_by_id(game_prog.card_id)
        if not card:
            raise HTTPException(status_code=404,
                                detail="Card not found")

        match choice:
            case 1:
                game_prog.humanity += card.first_human_delta
                game_prog.robotification += card.first_robot_delta
            case 2:
                game_prog.humanity += card.second_human_delta
                game_prog.robotification += card.second_robot_delta
            case _:
                raise HTTPException(status_code=400,
                                    detail="Wrong choice number")

        game_prog.step_number += 1
        ending = await self.level_end_rep.get_default_end_by_level(
            game_prog.level_id
        )

        if game_prog.step_number > await self.card_rep.count_by_level(
                game_prog.level_id
        ):
            game_prog.game_ended = True
            game_prog.level_ending_id = ending.id

        new_card = await self.card_rep.get_card_by_level_and_number(
            game_prog.level_id, game_prog.step_number
        )

        if new_card:
            game_prog.card_id = uuid.UUID(str(new_card.id))
        else:
            game_prog.step_number -= 1

        game_data = game_prog.model_dump()
        game_db = SGameProgressUpdate(**game_data)

        result_db = await self.game_prog_rep.update(game_db, game_prog.id)
        if result_db:
            result = SGameProgress.model_validate(result_db)
            return result
        else:
            raise HTTPException(status_code=400,
                                detail="Game progress was not changed")


async def get_game_progress_service(
    game_prog_rep: GameProgressRepository = Depends(get_game_progress_rep),
    card_rep: CardRepository = Depends(get_card_rep),
    level_end_rep: LevelEndingRepository = Depends(get_level_ending_rep)
):
    return GameProgressService(game_prog_rep,
                               card_rep,
                               level_end_rep)
