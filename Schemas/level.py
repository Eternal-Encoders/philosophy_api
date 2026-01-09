import uuid
from pydantic import Field, BaseModel, ConfigDict


class SLevelCreate(BaseModel):
    # number: int
    # text_section_id: uuid.UUID
    name: str | None = Field(max_length=200, default='')
    description: str | None = Field(max_length=1000,
                                    default='')
    model_config = ConfigDict(extra='forbid')


class SLevel(SLevelCreate):
    id: uuid.UUID
    model_config = ConfigDict(extra='forbid',
                              from_attributes=True)


class SLevelUpdate(BaseModel):
    # number: int | None = Field(ge=1)
    # text_section_id: uuid.UUID | None = Field(default=None)
    name: str | None = Field(max_length=200, default=None)
    description: str | None = Field(max_length=1000,
                                    default=None)
    model_config = ConfigDict(extra='forbid')
