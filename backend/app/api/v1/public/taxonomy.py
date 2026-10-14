"""前台公开接口：分类、标签（含文章计数）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_category, crud_tag
from app.db.session import get_db
from app.schemas import CategoryOut, TagOut

router = APIRouter(tags=["public-taxonomy"])


@router.get("/categories", response_model=list[CategoryOut], summary="分类列表")
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = await crud_category.list_with_count(db, published_only=True)
    return [
        CategoryOut(
            id=c.id, name=c.name, slug=c.slug, description=c.description,
            post_count=n, created_at=c.created_at,
        )
        for c, n in rows
    ]


@router.get("/tags", response_model=list[TagOut], summary="标签列表")
async def list_tags(db: AsyncSession = Depends(get_db)):
    rows = await crud_tag.list_with_count(db, published_only=True)
    return [
        TagOut(id=t.id, name=t.name, slug=t.slug, post_count=n, created_at=t.created_at)
        for t, n in rows
    ]
