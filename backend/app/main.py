"""FastAPI 应用入口。
启动：uvicorn app.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db

# ===== 日志配置 =====
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))

# 文件输出（按天轮转，保留 30 天）
file_handler = TimedRotatingFileHandler(
    filename=LOG_DIR / "app.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))

# 配置根日志器
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.info("📂 日志目录: %s", LOG_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 正在启动 %s ...", settings.APP_NAME)
    logger.info("📦 数据库初始化中...")
    await init_db()  # 自动建库建表 + 首次种子数据
    logger.info("✅ 数据库初始化完成")
    logger.info("🎉 %s 启动成功！", settings.APP_NAME)
    yield
    logger.info("👋 %s 正在关闭...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="XavierBlog 个人博客 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
logger.info("📡 API 路由已注册，前缀: /api/v1")


@app.get("/api/v1/health", tags=["health"], summary="健康检查")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


# 图片静态服务（挂载在路由之后，不影响 /api 前缀）
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
logger.info("📁 上传目录已挂载: %s", UPLOAD_DIR)
