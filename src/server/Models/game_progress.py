import uuid

from Models.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class GameProgressDB(Base):
    __tablename__ = "game_progress"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,
                                          default=uuid.uuid4)
    level_id: Mapped[uuid.UUID] = mapped_column(
      ForeignKey("level.id")
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
      ForeignKey("card.id")
    )
    game_ended: Mapped[bool]
    level_ending_id: Mapped[uuid.UUID | None] = mapped_column(
      ForeignKey("level_ending.id")
    )
    humanity: Mapped[int]
    robotification: Mapped[int]
    step_number: Mapped[int]

    level = relationship("LevelDB", back_populates="game_progresses")
    card = relationship("CardDB", back_populates="game_progresses")
    level_ending = relationship("LevelEndingDB",
                                back_populates="game_progresses")
