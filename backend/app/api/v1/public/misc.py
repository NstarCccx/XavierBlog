"""前台公开接口：评论发表与站点信息。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud import crud_comment, crud_post, crud_site
from app.db.session import get_db
from app.models import User
from app.schemas import CommentCreate, CommentOut, SiteInfo

router = APIRouter(tags=["public-misc"])


@router.get("/site-info", response_model=SiteInfo, summary="站点信息")
async def site_info(db: AsyncSession = Depends(get_db)):
    return SiteInfo(**await crud_site.get_all(db))


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[CommentOut],
    summary="文章已审核评论（树形）",
)
async def list_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud_post.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return await crud_comment.approved_tree(db, post_id)


@router.post("/comments", status_code=201, summary="发表评论（需登录，直接展示）")
async def create_comment(
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await crud_post.get_by_id(db, payload.post_id)
    if post is None or post.status != "published":
        raise HTTPException(status_code=404, detail="文章不存在")
    if payload.parent_id is not None:
        parent = await crud_comment.get(db, payload.parent_id)
        if parent is None or parent.post_id != payload.post_id:
            raise HTTPException(status_code=400, detail="被回复的评论不存在")
    comment = await crud_comment.create(
        db,
        post_id=payload.post_id,
        parent_id=payload.parent_id,
        user_id=user.id,
        nickname=user.nickname or user.username,
        email="",
        content=payload.content,
        is_author=user.role == "admin",
        status="approved",
    )
    return {"id": comment.id, "message": "评论已发表"}
