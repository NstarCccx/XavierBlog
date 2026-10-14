"""标签数据访问。"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, Tag, post_tags
from app.utils.slug import slugify


async def list_with_count(
    db: AsyncSession, published_only: bool = False
) -> list[tuple[Tag, int]]:
    """全部标签 + 各自文章数。"""
    count_cond = Post.status == "published" if published_only else True
    stmt = (
        select(Tag, func.count(post_tags.c.post_id))
        .outerjoin(post_tags, post_tags.c.tag_id == Tag.id)
        .outerjoin(Post, Post.id == post_tags.c.post_id)
        .where(count_cond)
        .group_by(Tag.id)
        .order_by(Tag.id)
    )
    result = await db.execute(stmt)
    return [(tag, count) for tag, count in result.all()]


async def get(db: AsyncSession, tag_id: int) -> Tag | None:
    return await db.get(Tag, tag_id)


async def get_by_name(db: AsyncSession, name: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.name == name))
    return result.scalar_one_or_none()


async def get_by_slug(db: AsyncSession, slug: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    return result.scalar_one_or_none()


async def get_or_create_many(db: AsyncSession, names: list[str]) -> list[Tag]:
    """按名称批量取标签，不存在则创建。"""
    tags: list[Tag] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        tag = await get_by_name(db, name)
        if tag is None:
            db.add(tag := Tag(name=name, slug=slugify(name) or f"tag-{len(tags)}"))
            await db.flush()
        tags.append(tag)
    return tags


async def unique_slug(db: AsyncSession, slug: str, exclude_id: int | None = None) -> str:
    base, n = slug, 1
    while True:
        stmt = select(Tag.id).where(Tag.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Tag.id != exclude_id)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if exists is None:
            return slug
        n += 1
        slug = f"{base}-{n}"


async def create(db: AsyncSession, *, name: str, slug: str | None) -> Tag:
    tag = Tag(name=name, slug=await unique_slug(db, slug or slugify(name)))
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update(db: AsyncSession, tag: Tag, *, name: str | None, slug: str | None) -> Tag:
    if name is not None:
        tag.name = name
    if slug is not None:
        tag.slug = await unique_slug(db, slugify(slug), exclude_id=tag.id)
    await db.commit()
    await db.refresh(tag)
    return tag


async def delete(db: AsyncSession, tag: Tag) -> None:
    await db.delete(tag)  # 多对多关联随 CASCADE 清理
    await db.commit()
