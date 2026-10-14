"""管理端仪表盘统计 + 站点设置。"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_comment, crud_site
from app.db.session import get_db
from app.models import Category, Comment, Post, Tag, User
from app.schemas import DashboardStats, PostViewsItem, SiteConfigUpdate

router = APIRouter(tags=["admin-misc"], dependencies=[Depends(get_current_admin)])


@router.get("/dashboard/stats", response_model=DashboardStats, summary="仪表盘统计")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    async def count(model, *conditions):
        stmt = select(func.count()).select_from(model)
        for cond in conditions:
            stmt = stmt.where(cond)
        return (await db.execute(stmt)).scalar_one()

    comment_total, comment_pending = await crud_comment.count_by_status(db)
    top_rows = (
        await db.execute(
            select(Post.id, Post.title, Post.views).order_by(Post.views.desc()).limit(10)
        )
    ).all()
    return DashboardStats(
        post_count=await count(Post),
        published_count=await count(Post, Post.status == "published"),
        draft_count=await count(Post, Post.status == "draft"),
        category_count=await count(Category),
        tag_count=await count(Tag),
        comment_count=comment_total,
        pending_comment_count=comment_pending,
        total_views=(await db.execute(select(func.coalesce(func.sum(Post.views), 0)))).scalar_one(),
        top_views=[PostViewsItem(id=r.id, title=r.title, views=r.views) for r in top_rows],
    )


@router.get("/site-config", summary="读取站点设置")
async def get_site_config(db: AsyncSession = Depends(get_db)):
    return await crud_site.get_all(db)


@router.put("/site-config", summary="保存站点设置")
async def update_site_config(
    payload: SiteConfigUpdate, db: AsyncSession = Depends(get_db)
):
    await crud_site.update_many(db, payload.data)
    return await crud_site.get_all(db)
