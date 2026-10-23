"""公开路由汇总。"""
from fastapi import APIRouter

from app.api.v1.public import auth, misc, posts, taxonomy

api_router = APIRouter()
api_router.include_router(posts.router)
api_router.include_router(taxonomy.router)
api_router.include_router(misc.router)
api_router.include_router(auth.router)
