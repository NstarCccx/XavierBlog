"""文章 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.category import CategoryBrief
from app.schemas.tag import TagBrief


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    summary: str = Field("", max_length=500)
    content: str = Field(min_length=1)
    cover: str = ""
    status: str = Field("draft", pattern="^(draft|published)$")
    is_pinned: bool = False
    category_id: int | None = None
    tag_ids: list[int] = []


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    summary: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)
    cover: str | None = None
    status: str | None = Field(None, pattern="^(draft|published)$")
    is_pinned: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostBrief(BaseModel):
    """列表页用：不含正文。"""

    model_config = {"from_attributes": True}

    id: int
    title: str
    slug: str
    summary: str
    cover: str
    status: str
    views: int
    is_pinned: bool = False
    published_at: datetime | None
    category: CategoryBrief | None = None
    tags: list[TagBrief] = []


class PostOut(PostBrief):
    """详情页/编辑用：含正文。"""

    content: str
    created_at: datetime
    updated_at: datetime


class ArchiveItem(BaseModel):
    """归档条目。"""

    model_config = {"from_attributes": True}

    id: int
    title: str
    slug: str
    published_at: datetime | None
    category: CategoryBrief | None = None
