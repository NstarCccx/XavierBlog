"""文章数据访问。"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Post, Tag, post_tags
from app.utils.slug import slugify


async def list_posts(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    category_slug: str | None = None,
    tag_slug: str | None = None,
    keyword: str | None = None,
) -> tuple[list[Post], int]:
    """分页查询文章，返回 (items, total)。前台默认只查已发布。"""
    conditions = []
    if status:
        conditions.append(Post.status == status)
    if category_slug:
        conditions.append(
            Post.category_id.in_(select(Category.id).where(Category.slug == category_slug))
        )
    if tag_slug:
        conditions.append(
            Post.id.in_(
                select(post_tags.c.post_id).where(
                    post_tags.c.tag_id.in_(
                        select(Tag.id).where(Tag.slug == tag_slug)
                    )
                )
            )
        )
    if keyword:
        conditions.append(Post.title.like(f"%{keyword}%"))

    base = select(Post)
    total_stmt = select(func.count()).select_from(Post)
    for cond in conditions:
        base = base.where(cond)
        total_stmt = total_stmt.where(cond)

    total = (await db.execute(total_stmt)).scalar_one()
    result = await db.execute(
        base.order_by(Post.is_pinned.desc(), Post.published_at.desc(), Post.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def archive(db: AsyncSession) -> list[Post]:
    """归档：全部已发布文章（仅取列表字段所需）。"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.category))
        .where(Post.status == "published")
        .order_by(Post.published_at.desc(), Post.id.desc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, post_id: int) -> Post | None:
    return await db.get(Post, post_id)


async def get_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(select(Post).where(Post.slug == slug))
    return result.scalar_one_or_none()


async def unique_slug(db: AsyncSession, slug: str, exclude_id: int | None = None) -> str:
    base, n = slug, 1
    while True:
        stmt = select(Post.id).where(Post.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Post.id != exclude_id)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if exists is None:
            return slug
        n += 1
        slug = f"{base}-{n}"


async def _attach_tags(db: AsyncSession, post: Post, tag_ids: list[int]) -> None:
    if not tag_ids:
        post.tags = []
        return
    result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    post.tags = list(result.scalars().all())


async def create(
    db: AsyncSession,
    *,
    title: str,
    slug: str | None,
    summary: str,
    content: str,
    cover: str,
    status: str,
    is_pinned: bool,
    category_id: int | None,
    tag_ids: list[int],
) -> Post:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    post = Post(
        title=title,
        slug=await unique_slug(db, slugify(slug or title)),
        summary=summary,
        content=content,
        cover=cover,
        status=status,
        is_pinned=is_pinned,
        category_id=category_id,
        published_at=now if status == "published" else None,
    )
    await _attach_tags(db, post, tag_ids)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update(db: AsyncSession, post: Post, *, fields: dict) -> Post:
    """部分更新；slug 与状态联动发布时间。"""
    tag_ids = fields.pop("tag_ids", None)

    if (status := fields.get("status")) is not None:
        if status == "published" and post.status != "published":
            fields.setdefault("published_at", datetime.now(timezone.utc).replace(tzinfo=None))

    if (slug := fields.get("slug")) is not None:
        fields["slug"] = await unique_slug(db, slugify(slug), exclude_id=post.id)

    for key, value in fields.items():
        setattr(post, key, value)

    if tag_ids is not None:
        await _attach_tags(db, post, tag_ids)

    await db.commit()
    await db.refresh(post)
    return post


async def delete(db: AsyncSession, post: Post) -> None:
    await db.delete(post)  # 评论随 CASCADE 删除
    await db.commit()


async def increment_views(db: AsyncSession, post: Post) -> None:
    post.views = post.views + 1
    await db.commit()
