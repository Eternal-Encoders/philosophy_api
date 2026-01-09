import uuid
from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Infrastructure.database import get_session
from Schemas.card import SCardCreate, SCardUpdate
from Models.card import CardDB


class CardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, card: SCardCreate) -> uuid.UUID:
        data = card.model_dump()
        new_card = CardDB(**data)
        self.session.add(new_card)
        await self.session.commit()
        await self.session.refresh(new_card)
        return new_card.id

    async def get_by_id(self, card_id: uuid.UUID) -> Optional[CardDB]:
        card = await self.session.execute(
            select(CardDB).where(CardDB.id == card_id)
        )
        return card.scalars().first()

    async def get_all(self):
        card = await self.session.execute(select(CardDB))
        return card.scalars().all()

    async def update(
            self,
            card_update: SCardUpdate,
            card_id: uuid.UUID
    ) -> Optional[CardDB]:
        card = await self.get_by_id(card_id)
        data = card_update.model_dump()
        if card:
            for key, value in data.items():
                if value:
                    setattr(card, key, value)
            await self.session.commit()
            await self.session.refresh(card)
        return card

    async def delete(self, card_id: uuid.UUID) -> bool:
        async with self.session as session:
            card = await self.get_by_id(card_id)
            if card:
                await session.delete(card)
                await session.commit()
                return True
            return False


async def get_card_rep(
    session: AsyncSession = Depends(get_session)
):
    return CardRepository(session)
