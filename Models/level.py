import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class LevelDB(Base):
    __tablename__ = "level"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,
                                          default=uuid.uuid4)
    # text_section_id: Mapped[uuid.UUID]
    # number: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]

    cards = relationship("CardDB",
                         back_populates="level",
                         cascade="all, delete-orphan")
    level_endings = relationship("LevelEndingDB",
                                 back_populates="level",
                                 cascade="all, delete-orphan")
    game_progresses = relationship("GameProgressDB",
                                   back_populates="level",
                                   cascade="all, delete-orphan")
