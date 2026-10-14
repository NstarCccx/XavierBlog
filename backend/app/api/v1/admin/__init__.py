"""管理路由汇总。各子路由已自带 prefix，这里不再重复指定。"""
from fastapi import APIRouter

from app.api.v1.admin import auth, comments, posts, taxonomy, uploads
from app.api.v1.admin.misc import router as misc_router

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(taxonomy.router)
api_router.include_router(comments.router)
api_router.include_router(uploads.router)
api_router.include_router(misc_router)
