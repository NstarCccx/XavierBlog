"""文章标签表 + 文章多对多关联表。"""
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

# 文章 <-> 标签 多对多关联表
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id",
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
        comment="文章 ID",
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        comment="标签 ID",
    ),
)


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="标签名")
    slug: Mapped[str] = mapped_column(String(50), unique=True, comment="URL 标识")

    posts: Mapped[list["Post"]] = relationship(  # 该标签下的文章
        secondary=post_tags, back_populates="tags"
    )
