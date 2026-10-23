"""管理端用户管理：列表、重置密码。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_user
from app.db.session import get_db
from app.models import User
from app.schemas import AdminResetPasswordRequest, PageResult, UserAdminOut

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("", response_model=PageResult[UserAdminOut], summary="用户分页")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    keyword: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    rows, total = await crud_user.admin_list(
        db, page=page, page_size=page_size, keyword=keyword
    )
    return PageResult(
        items=[UserAdminOut.model_validate(u) for u in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{user_id}/password", summary="重置用户密码")
async def reset_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = await crud_user.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    await crud_user.update_password(db, user, payload.new_password)
    return {"message": "密码已重置"}
