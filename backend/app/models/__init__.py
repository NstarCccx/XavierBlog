"""汇总导入全部模型：启动时 Base.metadata.create_all 建表依赖这里的完整注册。"""
from app.models.comment import Comment
from app.models.post import Post
from app.models.tag import Tag, post_tags
from app.models.category import Category
from app.models.site_config import SiteConfig
from app.models.user import User

__all__ = [
    "User",
    "Post",
    "Category",
    "Tag",
    "post_tags",
    "Comment",
    "SiteConfig",
]
