"""管理端图片上传与图库管理。本地存储在 backend/uploads/。"""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.deps import get_current_admin
from app.models import User

router = APIRouter(prefix="/uploads", tags=["admin-uploads"])

UPLOAD_DIR = Path(__file__).resolve().parents[4] / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


class UploadOut(BaseModel):
    url: str
    filename: str


class UploadItem(BaseModel):
    filename: str
    url: str
    size: int
    modified_at: datetime


def _safe_name(filename: str) -> Path | None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    sub_dir = datetime.now().strftime("%Y%m")
    return UPLOAD_DIR / sub_dir / f"{uuid.uuid4().hex}{ext}"


@router.post("", response_model=UploadOut, summary="上传图片")
async def upload_image(
    file: UploadFile, _: User = Depends(get_current_admin)
):
    dest = _safe_name(file.filename or "")
    if dest is None:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/gif/webp/svg 图片")
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    rel = dest.relative_to(UPLOAD_DIR).as_posix()
    return UploadOut(url=f"/uploads/{rel}", filename=dest.name)


@router.get("", response_model=list[UploadItem], summary="图库列表")
async def list_uploads(_: User = Depends(get_current_admin)):
    if not UPLOAD_DIR.exists():
        return []
    items = []
    for f in sorted(UPLOAD_DIR.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if not f.is_file() or f.name.startswith("."):
            continue
        st = f.stat()
        items.append(
            UploadItem(
                filename=f.name,
                url=f"/uploads/{f.relative_to(UPLOAD_DIR).as_posix()}",
                size=st.st_size,
                modified_at=datetime.fromtimestamp(st.st_mtime),
            )
        )
    return items


@router.get("/{path:path}", response_class=FileResponse, include_in_schema=False,
            summary="读取图片（仅开发备用；生产由 /uploads 静态挂载服务）")
async def read_upload(path: str):
    # 路径穿越防护：解析后的绝对路径必须仍在 uploads 内
    target = (UPLOAD_DIR / path).resolve()
    if not str(target).startswith(str(UPLOAD_DIR.resolve())) or not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(target)


@router.delete("", summary="删除图片")
async def delete_upload(url: str, _: User = Depends(get_current_admin)):
    rel = url.removeprefix("/uploads/").lstrip("/")
    target = (UPLOAD_DIR / rel).resolve()
    if not str(target).startswith(str(UPLOAD_DIR.resolve())) or not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    target.unlink()
    return {"message": "已删除"}
