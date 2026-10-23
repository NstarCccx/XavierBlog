"""用户表：管理员（admin）与前台注册用户（member）共用。"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, comment="登录名")
    hashed_password: Mapped[str] = mapped_column(String(128), comment="bcrypt 哈希")
    nickname: Mapped[str] = mapped_column(String(50), default="", comment="显示昵称")
    avatar: Mapped[str] = mapped_column(String(255), default="", comment="头像 URL")
    role: Mapped[str] = mapped_column(String(20), default="member", comment="角色：admin 管理员 / member 注册用户")
