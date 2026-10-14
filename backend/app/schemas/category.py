"""分类 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    slug: str | None = Field(None, max_length=50)
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    slug: str | None = Field(None, max_length=50)
    description: str | None = None


class CategoryBrief(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategoryOut(CategoryBrief):
    description: str
    post_count: int = 0
    created_at: datetime
