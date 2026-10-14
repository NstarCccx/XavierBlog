"""前台公开接口：文章。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_post
from app.db.session import get_db
from app.schemas import ArchiveItem, PageResult, PostBrief, PostOut

router = APIRouter(prefix="/posts", tags=["public-posts"])


@router.get("", response_model=PageResult[PostBrief], summary="已发布文章分页")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: str | None = Query(None, description="按分类 slug 筛选"),
    tag: str | None = Query(None, description="按标签 slug 筛选"),
    keyword: str | None = Query(None, description="标题关键词"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud_post.list_posts(
        db,
        page=page,
        page_size=page_size,
        status="published",
        category_slug=category,
        tag_slug=tag,
        keyword=keyword,
    )
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.get("/archive", response_model=list[ArchiveItem], summary="归档时间线")
async def archive(db: AsyncSession = Depends(get_db)):
    return await crud_post.archive(db)


@router.get("/{slug}", response_model=PostOut, summary="文章详情（浏览量 +1）")
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    post = await crud_post.get_by_slug(db, slug)
    if post is None or post.status != "published":
        raise HTTPException(status_code=404, detail="文章不存在")
    await crud_post.increment_views(db, post)
    return post
