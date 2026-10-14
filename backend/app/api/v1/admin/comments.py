"""管理端评论：列表、审核、回复、删除。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_comment
from app.db.session import get_db
from app.models import User
from app.schemas import CommentAdminOut, CommentReplyCreate, PageResult

router = APIRouter(prefix="/comments", tags=["admin-comments"])


def _to_out(comment, post_title: str) -> CommentAdminOut:
    return CommentAdminOut(
        id=comment.id,
        post_id=comment.post_id,
        post_title=post_title,
        parent_id=comment.parent_id,
        nickname=comment.nickname,
        email=comment.email,
        content=comment.content,
        status=comment.status,
        is_author=comment.is_author,
        created_at=comment.created_at,
    )


@router.get("", response_model=PageResult[CommentAdminOut], summary="评论分页")
async def list_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: str | None = Query(None, pattern="^(pending|approved)$"),
    keyword: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    rows, total = await crud_comment.admin_list(
        db, page=page, page_size=page_size, status=status, keyword=keyword
    )
    items = [_to_out(c, title) for c, title in rows]
    return PageResult(items=items, total=total, page=page, page_size=page_size)


@router.put("/{comment_id}/approve", summary="通过评论")
async def approve_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)
):
    comment = await crud_comment.get(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    await crud_comment.set_status(db, comment, "approved")
    return {"message": "已通过"}


@router.put("/{comment_id}/reject", summary="拒绝（退回待审核）")
async def reject_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)
):
    comment = await crud_comment.get(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    await crud_comment.set_status(db, comment, "pending")
    return {"message": "已退回待审核"}


@router.delete("/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)
):
    comment = await crud_comment.get(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    await crud_comment.delete(db, comment)
    return {"message": "已删除"}


@router.post("/{comment_id}/reply", status_code=201, summary="以博主身份回复评论")
async def reply_comment(
    comment_id: int,
    payload: CommentReplyCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    parent = await crud_comment.get(db, comment_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    reply = await crud_comment.create(
        db,
        post_id=parent.post_id,
        parent_id=parent.id,
        nickname=admin.nickname or admin.username,
        email="",
        content=payload.content,
        is_author=True,
        status="approved",  # 博主回复直接通过
    )
    # 父评论若还是待审核，一并放行，保证回复可见
    if parent.status == "pending":
        await crud_comment.set_status(db, parent, "approved")
    return {"id": reply.id, "message": "回复成功"}
