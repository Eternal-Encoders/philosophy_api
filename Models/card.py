import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class CardDB(Base):
    __tablename__ = "card"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,
                                          default=uuid.uuid4)
    level_id: Mapped[uuid.UUID] = mapped_column(
       ForeignKey("level.id")
    )
    number: Mapped[int]
    name: Mapped[str]
    text: Mapped[str]
    first_choice_text: Mapped[str]
    second_choice_text: Mapped[str]
    first_human_delta: Mapped[int]
    second_human_delta: Mapped[int]
    first_robot_delta: Mapped[int]
    second_robot_delta: Mapped[int]
    image_link: Mapped[str] = mapped_column(
       default=""
    )

    level = relationship("LevelDB",
                         back_populates="cards")
    game_progresses = relationship("GameProgressDB",
                                   back_populates="card",
                                   cascade="all, delete-orphan")
