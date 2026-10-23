"""FastAPI 依赖注入：数据库会话、JWT 用户鉴权（前台 member 与后台 admin 共用 users 表）。"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.crud import crud_user
from app.db.session import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    """校验 Bearer Token，返回当前登录用户（不限角色）；失败返回 401。"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    username = decode_access_token(credentials.credentials)
    if username is None:
        raise unauthorized
    user = await crud_user.get_by_username(db, username)
    if user is None:
        raise unauthorized
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """在登录基础上要求管理员角色；普通用户 token 返回 403。"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return user
