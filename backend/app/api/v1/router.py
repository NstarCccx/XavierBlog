"""API v1 总路由：public + admin。"""
from fastapi import APIRouter

from app.api.v1 import admin, public

api_router = APIRouter()
api_router.include_router(public.api_router)
api_router.include_router(admin.api_router, prefix="/admin")
