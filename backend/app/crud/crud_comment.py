"""评论数据访问。"""
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment, Post


async def create(
    db: AsyncSession,
    *,
    post_id: int,
    parent_id: int | None,
    nickname: str,
    email: str,
    content: str,
    is_author: bool = False,
    status: str = "pending",
) -> Comment:
    comment = Comment(
        post_id=post_id,
        parent_id=parent_id,
        nickname=nickname,
        email=email,
        content=content,
        is_author=is_author,
        status=status,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def approved_tree(db: AsyncSession, post_id: int) -> list[dict]:
    """某文章已通过审核的评论，组装为二级树（顶级 + replies）。

    返回普通字典而非 ORM 对象，避免异步环境下自引用关系触发懒加载。
    """
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.status == "approved")
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    comments = list(result.scalars().all())

    children: dict[int | None, list[Comment]] = defaultdict(list)
    for c in comments:
        children[c.parent_id].append(c)

    def build(parent_id: int | None) -> list[dict]:
        return [
            {
                "id": c.id,
                "nickname": c.nickname,
                "content": c.content,
                "is_author": c.is_author,
                "created_at": c.created_at,
                "replies": build(c.id),
            }
            for c in children.get(parent_id, [])
        ]

    return build(None)


async def admin_list(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    keyword: str | None = None,
) -> tuple[list[tuple[Comment, str]], int]:
    """后台评论分页，附带所属文章标题。"""
    conditions = []
    if status:
        conditions.append(Comment.status == status)
    if keyword:
        conditions.append(
            Comment.content.like(f"%{keyword}%") | Comment.nickname.like(f"%{keyword}%")
        )

    base = (
        select(Comment, Post.title)
        .outerjoin(Post, Comment.post_id == Post.id)
    )
    total_stmt = select(func.count()).select_from(Comment)
    for cond in conditions:
        base = base.where(cond)
        total_stmt = total_stmt.where(cond)

    total = (await db.execute(total_stmt)).scalar_one()
    result = await db.execute(
        base.order_by(Comment.created_at.desc(), Comment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return [(c, title or "") for c, title in result.all()], total


async def get(db: AsyncSession, comment_id: int) -> Comment | None:
    return await db.get(Comment, comment_id)


async def set_status(db: AsyncSession, comment: Comment, status: str) -> Comment:
    comment.status = status
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete(db: AsyncSession, comment: Comment) -> None:
    await db.delete(comment)
    await db.commit()


async def count_by_status(db: AsyncSession) -> tuple[int, int]:
    """返回 (总数, 待审核数)。"""
    total = (await db.execute(select(func.count()).select_from(Comment))).scalar_one()
    pending = (
        await db.execute(
            select(func.count())
            .select_from(Comment)
            .where(Comment.status == "pending")
        )
    ).scalar_one()
    return total, pending
