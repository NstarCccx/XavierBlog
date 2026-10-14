"""管理端认证：登录、当前用户、修改密码。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.security import create_access_token, verify_password
from app.crud import crud_user
from app.db.session import get_db
from app.models import User
from app.schemas import AdminInfo, ChangePasswordRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["admin-auth"])


@router.post("/login", response_model=TokenResponse, summary="登录获取 Token")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenResponse(access_token=create_access_token(user.username))


@router.get("/me", response_model=AdminInfo, summary="当前管理员信息")
async def me(admin: User = Depends(get_current_admin)):
    return admin


@router.put("/password", summary="修改密码")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not verify_password(payload.old_password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    await crud_user.update_password(db, admin, payload.new_password)
    return {"message": "密码已修改，请重新登录"}
