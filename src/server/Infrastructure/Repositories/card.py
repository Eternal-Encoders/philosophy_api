import uuid

from fastapi import Depends
from Infrastructure.database import get_session
from Infrastructure.generic_repository import GenericRepository
from Models.card import CardDB
from Schemas.card import SCardCreate, SCardUpdate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CardRepository(GenericRepository[CardDB, SCardCreate, SCardUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(CardDB, session)

    async def count_by_level(self, level_id: uuid.UUID):
        async with self.session as session:
            query = select(func.count()).select_from(self.model)
            query = query.where(CardDB.level_id == level_id)
            result = await session.execute(query)
            return result.scalar_one()

    async def get_numbers_by_level(self, level_id) -> list[int]:
        query = select(CardDB.number) \
            .where(CardDB.level_id == level_id) \
            .order_by(CardDB.number)
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_card_by_level_and_number(
            self,
            level_id: uuid.UUID,
            number: int,
    ) -> CardDB | None:
        query = select(CardDB) \
            .where(CardDB.level_id == level_id,
                   CardDB.number == number)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def shift_cards_number(
            self,
            level_id: uuid.UUID,
            after_number: int
    ):
        query = select(CardDB).where(
            CardDB.level_id == level_id,
            CardDB.number >= after_number
        ).order_by(CardDB.number)
        result = await self.session.execute(query)
        cards_to_shift = result.scalars().all()

        if not cards_to_shift:
            return

        for card in cards_to_shift:
            card.number += 1

        await self.session.flush()


async def get_card_rep(
    session: AsyncSession | None = None
):
    if session is None:
        session = Depends(get_session)
    assert session is not None

    return CardRepository(session)
