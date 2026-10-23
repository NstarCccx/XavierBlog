"""认证 DTO。"""
from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    """前台用户注册：用户名 + 昵称 + 密码。"""

    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    nickname: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=6, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """前台登录用户信息。"""

    id: int
    username: str
    nickname: str
    avatar: str
    role: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """前台登录/注册：token + 用户信息，一次返回省去再请求 me。"""

    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)


class AdminInfo(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str

    model_config = {"from_attributes": True}


class UserAdminOut(BaseModel):
    """管理端用户列表项。"""

    id: int
    username: str
    nickname: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminResetPasswordRequest(BaseModel):
    """管理员重置用户密码：直接下发新密码，无需原密码。"""

    new_password: str = Field(min_length=6, max_length=128)
