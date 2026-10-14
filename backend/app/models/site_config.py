"""站点设置表：键值对（站名、简介、关于页、页脚等）。"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SiteConfig(Base):
    __tablename__ = "site_configs"

    key: Mapped[str] = mapped_column(String(50), primary_key=True, comment="配置键")
    value: Mapped[str] = mapped_column(Text, default="", comment="配置值")
