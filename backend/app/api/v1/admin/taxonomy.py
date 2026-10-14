"""管理端分类 / 标签 CRUD。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_category, crud_tag
from app.db.session import get_db
from app.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    TagCreate,
    TagOut,
    TagUpdate,
)

router = APIRouter(tags=["admin-taxonomy"], dependencies=[Depends(get_current_admin)])


# ---------- 分类 ----------
@router.get("/categories", response_model=list[CategoryOut], summary="分类列表（含文章数）")
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = await crud_category.list_with_count(db)
    return [
        CategoryOut(
            id=c.id, name=c.name, slug=c.slug, description=c.description,
            post_count=n, created_at=c.created_at,
        )
        for c, n in rows
    ]


@router.post("/categories", response_model=CategoryOut, status_code=201, summary="新建分类")
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    if await crud_category.get_by_name(db, payload.name):
        raise HTTPException(status_code=400, detail="分类名已存在")
    c = await crud_category.create(
        db, name=payload.name, slug=payload.slug, description=payload.description
    )
    return CategoryOut(
        id=c.id, name=c.name, slug=c.slug, description=c.description,
        post_count=0, created_at=c.created_at,
    )


@router.put("/categories/{category_id}", response_model=CategoryOut, summary="更新分类")
async def update_category(
    category_id: int, payload: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    category = await crud_category.get(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    fields = payload.model_dump(exclude_unset=True)
    category = await crud_category.update(db, category, **fields)
    return CategoryOut(
        id=category.id, name=category.name, slug=category.slug,
        description=category.description, post_count=0, created_at=category.created_at,
    )


@router.delete("/categories/{category_id}", summary="删除分类")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud_category.get(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    await crud_category.delete(db, category)
    return {"message": "已删除"}


# ---------- 标签 ----------
@router.get("/tags", response_model=list[TagOut], summary="标签列表（含文章数）")
async def list_tags(db: AsyncSession = Depends(get_db)):
    rows = await crud_tag.list_with_count(db)
    return [
        TagOut(id=t.id, name=t.name, slug=t.slug, post_count=n, created_at=t.created_at)
        for t, n in rows
    ]


@router.post("/tags", response_model=TagOut, status_code=201, summary="新建标签")
async def create_tag(payload: TagCreate, db: AsyncSession = Depends(get_db)):
    if await crud_tag.get_by_name(db, payload.name):
        raise HTTPException(status_code=400, detail="标签名已存在")
    t = await crud_tag.create(db, name=payload.name, slug=payload.slug)
    return TagOut(id=t.id, name=t.name, slug=t.slug, post_count=0, created_at=t.created_at)


@router.put("/tags/{tag_id}", response_model=TagOut, summary="更新标签")
async def update_tag(tag_id: int, payload: TagUpdate, db: AsyncSession = Depends(get_db)):
    tag = await crud_tag.get(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    fields = payload.model_dump(exclude_unset=True)
    tag = await crud_tag.update(db, tag, **fields)
    return TagOut(id=tag.id, name=tag.name, slug=tag.slug, post_count=0, created_at=tag.created_at)


@router.delete("/tags/{tag_id}", summary="删除标签")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await crud_tag.get(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    await crud_tag.delete(db, tag)
    return {"message": "已删除"}
