"""文章分类表。"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名")
    slug: Mapped[str] = mapped_column(String(50), unique=True, comment="URL 标识")
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")

    posts: Mapped[list["Post"]] = relationship(  # 该分类下的文章
        back_populates="category"
    )
