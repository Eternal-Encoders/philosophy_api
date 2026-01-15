import uuid

from pydantic import BaseModel, ConfigDict, Field


class SCardCreate(BaseModel):
    level_id: uuid.UUID
    number: int = Field(ge=1)
    name: str | None = Field(max_length=200, default='')
    text: str | None = Field(max_length=1000, default='')
    first_choice_text: str | None = Field(max_length=500,
                                          default='')
    second_choice_text: str | None = Field(max_length=500,
                                           default='')
    first_human_delta: int = Field(ge=-100, le=100,
                                   default=0)
    second_human_delta: int = Field(ge=-100,
                                    le=100,
                                    default=0)
    first_robot_delta: int = Field(ge=-100,
                                   le=100,
                                   default=0)
    second_robot_delta: int = Field(ge=-100,
                                    le=100,
                                    default=0)
    image_link: str | None = ''
    model_config = ConfigDict(extra='forbid')


class SCard(SCardCreate):
    id: uuid.UUID
    model_config = ConfigDict(extra='forbid',
                              from_attributes=True)


class SCardUpdate(BaseModel):
    level_id: uuid.UUID | None
    number: int | None = Field(ge=1, default=None)
    name: str | None = Field(max_length=200,
                             default=None)
    text: str | None = Field(max_length=1000,
                             default=None)
    first_choice_text: str | None = Field(max_length=500,
                                          default=None)
    second_choice_text: str | None = Field(max_length=500,
                                           default=None)
    first_human_delta: int | None = Field(ge=-100, le=100,
                                          default=None)
    second_human_delta: int | None = Field(ge=-100, le=100,
                                           default=None)
    first_robot_delta: int | None = Field(ge=-100, le=100,
                                          default=None)
    second_robot_delta: int | None = Field(ge=-100, le=100,
                                           default=None)
    image_link: str | None
    model_config = ConfigDict(extra='forbid')
