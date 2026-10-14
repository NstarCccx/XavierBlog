"""slug 工具：从标题生成 URL 友好标识。"""
import re
import unicodedata
import uuid


def slugify(text: str) -> str:
    """生成 slug：保留字母数字与连字符；中文等被移除后为空则回退随机串。"""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)[:80]
    return text or f"post-{uuid.uuid4().hex[:8]}"
