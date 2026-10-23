"""前台用户认证：注册、登录、当前用户。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import crud_user
from app.db.session import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, UserInfo

router = APIRouter(prefix="/auth", tags=["public-auth"])


@router.post("/register", response_model=AuthResponse, status_code=201, summary="注册用户")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await crud_user.get_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="用户名已被注册")
    user = await crud_user.create(
        db,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        nickname=payload.nickname,
        role="member",
    )
    return AuthResponse(
        access_token=create_access_token(user.username), user=UserInfo.model_validate(user)
    )


@router.post("/login", response_model=AuthResponse, summary="登录获取 Token")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return AuthResponse(
        access_token=create_access_token(user.username), user=UserInfo.model_validate(user)
    )


@router.get("/me", response_model=UserInfo, summary="当前登录用户")
async def me(user: User = Depends(get_current_user)):
    return user
