import uuid

from pydantic import BaseModel, ConfigDict, Field


class SLevelEndingCreate(BaseModel):
    level_id: uuid.UUID
    name: str = Field(max_length=200, default="")
    description: str = Field(max_length=1000, default="")
    image_link: str = Field(default="")
    robot_condition: int = Field(default=0)
    human_condition: int = Field(default=0)
    is_default: bool = Field(default=False)
    model_config = ConfigDict(extra="forbid")


class SLevelEnding(SLevelEndingCreate):
    id: uuid.UUID
    model_config = ConfigDict(extra="forbid",
                              from_attributes=True)


class SLevelEndingUpdate(BaseModel):
    level_id: uuid.UUID | None
    name: str | None = Field(max_length=200, default=None)
    description: str | None = Field(max_length=1000, default=None)
    image_link: str | None = Field(default=None)
    robot_condition: int | None = None
    human_condition: int | None = None
    is_default: bool | None = Field(default=None)
    model_config = ConfigDict(extra="forbid")
