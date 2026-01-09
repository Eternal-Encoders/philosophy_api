import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Models import Base


class LevelEndingDB(Base):
    __tablename__ = "level_ending"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,
                                          default=uuid.uuid4)
    level_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("level.id")
    )
    name: Mapped[str]
    description: Mapped[str]
    image_link: Mapped[str]
    robot_condition: Mapped[int]
    human_condition: Mapped[int]
    is_default: Mapped[bool]

    level = relationship(
        "LevelDB",
        back_populates="level_endings")
    game_progresses = relationship(
        "GameProgressDB",
        back_populates="level_ending"
    )
