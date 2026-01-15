import uuid

from fastapi import Depends, HTTPException
from Infrastructure.Repositories.card import CardRepository, get_card_rep
from Schemas.card import SCard, SCardCreate


class CardService:
    def __init__(
            self,
            card_rep: CardRepository
    ):
        self.card_rep = card_rep

    async def create_card(self, card: SCardCreate):
        if card.number < 1:
            raise HTTPException(
                status_code=400,
                detail="Card number is less than 1"
            )

        count = await self.card_rep.count_by_level(card.level_id)
        if count >= card.number:
            await self.card_rep.shift_cards_number(card.level_id, card.number)

        numbers = await self.card_rep.get_numbers_by_level(card.level_id)
        numbers.append(card.number)
        numbers.sort()
        counter = 1

        for number in numbers:
            if number != counter:
                await self.card_rep.session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"There is no card with number {counter}"
                )
            counter += 1

        card_db = await self.card_rep.create(card)
        if card_db:
            return SCard.model_validate(card_db)
        else:
            raise HTTPException(status_code=400,
                                detail="Card was not created")

    async def get_card_by_id(self, card_id: uuid.UUID):
        card_db = await self.card_rep.get_by_id(card_id)
        if card_db:
            return SCard.model_validate(card_db)
        else:
            raise HTTPException(status_code=404,
                                detail="Card not found")

    async def get_all_cards(self):
        cards_db = await self.card_rep.get_all()
        return [SCard.model_validate(card_db) for card_db in cards_db]

    # async def update_card(self,
    #                       new_card: SCardUpdate,
    #                       card_id: uuid.UUID):
    #     old_card = await self.get_card_by_id(card_id)
    #     if new_card.number:
    #         if new_card.number < 1:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="Card number is less than 1"
    #             )
    #         if new_card.level_id:
    #             if new_card.number > await self.card_rep.count_by_level(
    #                     new_card.level_id
    #             ):
    #                 raise HTTPException(
    #                     status_code=400,
    #                     detail="Card number is too high"
    #                 )
    #         else:
    #             if new_card.number > await self.card_rep.count_by_level(
    #                 old_card.level_id
    #             ):
    #                 raise HTTPException(
    #                     status_code=400,
    #                     detail="Card number is too high"
    #                 )
    #
    #     card_db = await self.card_rep.update(new_card,
    #                                          card_id)
    #     if card_db:
    #         return SCard.model_validate(card_db)
    #     else:
    #         raise HTTPException(status_code=404,
    #                             detail="Card not found")

    async def delete_card(self, card_id: uuid.UUID):
        if not await self.card_rep.delete(card_id):
            raise HTTPException(status_code=404,
                                detail="Card not found")


async def get_card_service(
    card_rep: CardRepository | None = None
):
    if card_rep is None:
        card_rep = Depends(get_card_rep)
    assert card_rep is not None

    return CardService(card_rep)
