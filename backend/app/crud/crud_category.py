"""分类数据访问。"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Post
from app.utils.slug import slugify


async def list_with_count(
    db: AsyncSession, published_only: bool = False
) -> list[tuple[Category, int]]:
    """全部分类 + 各自文章数（published_only 时只统计已发布文章）。"""
    stmt = (
        select(Category, func.count(Post.id))
        .outerjoin(Post, Post.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.id)
    )
    if published_only:
        stmt = stmt.where(Post.status == "published")
    result = await db.execute(stmt)
    return [(cat, count) for cat, count in result.all()]


async def get(db: AsyncSession, category_id: int) -> Category | None:
    return await db.get(Category, category_id)


async def get_by_slug(db: AsyncSession, slug: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.name == name))
    return result.scalar_one_or_none()


async def unique_slug(db: AsyncSession, slug: str, exclude_id: int | None = None) -> str:
    """slug 冲突时追加 -2/-3…，保证唯一。"""
    base, n = slug, 1
    while True:
        stmt = select(Category.id).where(Category.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if exists is None:
            return slug
        n += 1
        slug = f"{base}-{n}"


async def create(
    db: AsyncSession, *, name: str, slug: str | None, description: str = ""
) -> Category:
    category = Category(
        name=name,
        slug=await unique_slug(db, slug or slugify(name)),
        description=description,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update(
    db: AsyncSession,
    category: Category,
    *,
    name: str | None,
    slug: str | None,
    description: str | None,
) -> Category:
    if name is not None:
        category.name = name
    if slug is not None:
        category.slug = await unique_slug(db, slugify(slug), exclude_id=category.id)
    if description is not None:
        category.description = description
    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)  # 文章的 category_id 由外键 SET NULL 兜底
    await db.commit()
