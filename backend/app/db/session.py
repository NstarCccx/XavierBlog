"""数据库会话：async engine、会话工厂、连接前自动建库。"""
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


def _server_url() -> str:
    """不带库名的连接串，用于 CREATE DATABASE。"""
    return (
        f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/?charset=utf8mb4"
    )


async def ensure_database() -> None:
    """目标库不存在时自动创建（utf8mb4），免去手工建库步骤。"""
    engine = create_async_engine(_server_url(), isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
        logger.info("数据库 %s 已就绪", settings.DB_NAME)
    finally:
        await engine.dispose()


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG and False,  # 需要看 SQL 时改 True
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：每个请求一个会话，结束自动归还。"""
    async with AsyncSessionLocal() as session:
        yield session
