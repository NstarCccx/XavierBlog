"""文章表。"""
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.tag import post_tags


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    title: Mapped[str] = mapped_column(String(200), comment="标题")
    slug: Mapped[str] = mapped_column(String(200), unique=True, comment="URL 标识")
    summary: Mapped[str] = mapped_column(String(500), default="", comment="摘要")
    content: Mapped[str] = mapped_column(Text, comment="Markdown 正文")
    cover: Mapped[str] = mapped_column(String(255), default="", comment="封面图 URL")
    status: Mapped[str] = mapped_column(
        Enum("draft", "published", name="post_status"),
        default="draft",
        comment="状态：草稿/已发布",
    )
    views: Mapped[int] = mapped_column(Integer, default=0, comment="浏览量")
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), comment="发布时间"
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), comment="分类"
    )
    category: Mapped["Category | None"] = relationship(  # 所属分类
        back_populates="posts", lazy="selectin"
    )
    tags: Mapped[list["Tag"]] = relationship(  # 所属标签列表
        secondary=post_tags, back_populates="posts", lazy="selectin"
    )
    # 评论不建 ORM 关系：异步环境下避免懒加载，统一走 crud_comment 显式查询
