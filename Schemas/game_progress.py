import uuid
from pydantic import Field, BaseModel, ConfigDict
from Schemas.level_ending import SLevelEnding


class SGameProgressCreate(BaseModel):
    level_id: uuid.UUID
    card_id: uuid.UUID
    game_ended: bool = Field(default=False)
    step_number: int = Field(default=1, ge=1)
    level_ending_id: uuid.UUID | None = Field(default=None)
    humanity: int = Field(default=50, ge=0, le=100)
    robotification: int = Field(default=50, ge=0, le=100)
    model_config = ConfigDict(extra='forbid')


class SGameProgressCreateDto(BaseModel):
    level_id: uuid.UUID
    model_config = ConfigDict(extra='forbid')


class SGameProgress(SGameProgressCreate):
    id: uuid.UUID

    model_config = ConfigDict(extra='forbid',
                              from_attributes=True)


class SGameProgressUpdate(BaseModel):
    level_id: uuid.UUID | None = None
    card_id: uuid.UUID | None = None
    game_ended: bool | None = None
    level_ending_id: uuid.UUID | None = None
    humanity: int = Field(None, ge=0, le=100)
    robotification: int = Field(None, ge=0, le=100)
    step_number: int = Field(None, ge=1)
    model_config = ConfigDict(extra='ignore')


class SGameProgressRead(SGameProgress):
    level_ending: SLevelEnding | None = Field(None)
    model_config = ConfigDict(extra='ignore')
