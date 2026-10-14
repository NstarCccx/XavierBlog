"""标签 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    slug: str | None = Field(None, max_length=50)


class TagUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    slug: str | None = Field(None, max_length=50)


class TagBrief(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class TagOut(TagBrief):
    post_count: int = 0
    created_at: datetime
