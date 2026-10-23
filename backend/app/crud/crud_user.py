"""用户数据访问。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def create(
    db: AsyncSession,
    *,
    username: str,
    hashed_password: str,
    nickname: str,
    role: str = "member",
) -> User:
    user = User(
        username=username,
        hashed_password=hashed_password,
        nickname=nickname,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(db: AsyncSession, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def update_profile(
    db: AsyncSession, user: User, nickname: str, avatar: str
) -> User:
    user.nickname = nickname
    user.avatar = avatar
    await db.commit()
    await db.refresh(user)
    return user
