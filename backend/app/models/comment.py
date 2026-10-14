"""评论表：支持二级回复、审核状态。"""
from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), comment="所属文章"
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), comment="父评论（回复）"
    )
    nickname: Mapped[str] = mapped_column(String(50), comment="评论者昵称")
    email: Mapped[str] = mapped_column(String(100), default="", comment="评论者邮箱")
    content: Mapped[str] = mapped_column(Text, comment="评论内容")
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", name="comment_status"),
        default="pending",
        comment="状态：待审核/已通过",
    )
    is_author: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否博主回复"
    )
