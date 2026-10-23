"""DTO 汇总导出。"""
from app.schemas.auth import (
    AdminInfo,
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserInfo,
)
from app.schemas.category import CategoryBrief, CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.comment import CommentAdminOut, CommentCreate, CommentOut, CommentReplyCreate
from app.schemas.common import PageResult
from app.schemas.post import ArchiveItem, PostBrief, PostCreate, PostOut, PostUpdate
from app.schemas.site import DashboardStats, PostViewsItem, SiteConfigUpdate, SiteInfo
from app.schemas.tag import TagBrief, TagCreate, TagOut, TagUpdate

__all__ = [
    "AdminInfo",
    "AuthResponse",
    "ChangePasswordRequest",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserInfo",
    "CategoryBrief",
    "CategoryCreate",
    "CategoryOut",
    "CategoryUpdate",
    "CommentAdminOut",
    "CommentCreate",
    "CommentOut",
    "CommentReplyCreate",
    "PageResult",
    "ArchiveItem",
    "PostBrief",
    "PostCreate",
    "PostOut",
    "PostUpdate",
    "DashboardStats",
    "PostViewsItem",
    "SiteConfigUpdate",
    "SiteInfo",
    "TagBrief",
    "TagCreate",
    "TagOut",
    "TagUpdate",
]
