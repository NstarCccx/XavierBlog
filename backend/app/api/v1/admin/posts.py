"""管理端文章 CRUD。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_post
from app.db.session import get_db
from app.models import User
from app.schemas import PageResult, PostBrief, PostCreate, PostOut, PostUpdate

router = APIRouter(prefix="/posts", tags=["admin-posts"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=PageResult[PostBrief], summary="文章分页（含草稿）")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: str | None = Query(None, pattern="^(draft|published)$"),
    keyword: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud_post.list_posts(
        db, page=page, page_size=page_size, status=status, keyword=keyword
    )
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=PostOut, status_code=201, summary="新建文章")
async def create_post(payload: PostCreate, db: AsyncSession = Depends(get_db)):
    return await crud_post.create(db, **payload.model_dump())


@router.get("/{post_id}", response_model=PostOut, summary="文章详情")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud_post.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.put("/{post_id}", response_model=PostOut, summary="更新文章")
async def update_post(
    post_id: int, payload: PostUpdate, db: AsyncSession = Depends(get_db)
):
    post = await crud_post.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    fields = payload.model_dump(exclude_unset=True)
    return await crud_post.update(db, post, fields=fields)


@router.delete("/{post_id}", summary="删除文章")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud_post.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    await crud_post.delete(db, post)
    return {"message": "已删除"}
