"""用户数据访问。"""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def admin_list(
    db: AsyncSession, *, page: int, page_size: int, keyword: str | None = None
) -> tuple[list[User], int]:
    """管理端用户分页：keyword 模糊匹配用户名或昵称。"""
    stmt = select(User)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(User.username.ilike(like), User.nickname.ilike(like)))
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (
        await db.execute(stmt.order_by(User.id).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return list(rows), total


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
