"""评论 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """登录用户发表评论：昵称等身份信息由服务端取自当前账号。"""

    post_id: int
    parent_id: int | None = None
    content: str = Field(min_length=1, max_length=2000)


class CommentReplyCreate(BaseModel):
    """博主回复评论。"""

    content: str = Field(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    """前台展示：仅已通过审核的，含二级回复。"""

    model_config = {"from_attributes": True}

    id: int
    nickname: str
    content: str
    is_author: bool
    created_at: datetime
    replies: list["CommentOut"] = []


class CommentAdminOut(BaseModel):
    """后台管理列表。"""

    id: int
    post_id: int
    post_title: str
    parent_id: int | None
    nickname: str
    email: str
    content: str
    status: str
    is_author: bool
    created_at: datetime
