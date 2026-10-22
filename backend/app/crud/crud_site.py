"""站点设置数据访问：键值对读写。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SiteConfig

DEFAULTS: dict[str, str] = {
    "site_name": "XavierBlog",
    "site_description": "一个用 FastAPI + Vue3 搭建的个人博客",
    "about_content": "## 关于我\n\n这里填写关于页内容（支持 Markdown）。",
    "footer": "© 2026 XavierBlog · Powered by FastAPI + Vue3",
    # 备案信息：ICP 已备案，公安备案号码待下发（留空时前台不展示）
    "icp_number": "粤ICP备2026162376号",
    "icp_link": "https://beian.miit.gov.cn/",
    "police_number": "",
    "police_link": "",
}


async def get_all(db: AsyncSession) -> dict[str, str]:
    result = await db.execute(select(SiteConfig))
    stored = {row.key: row.value for row in result.scalars().all()}
    return {**DEFAULTS, **stored}


async def update_many(db: AsyncSession, data: dict[str, str]) -> None:
    """批量 upsert。"""
    result = await db.execute(
        select(SiteConfig).where(SiteConfig.key.in_(data.keys()))
    )
    existing = {row.key: row for row in result.scalars().all()}
    for key, value in data.items():
        if key in existing:
            existing[key].value = value
        else:
            db.add(SiteConfig(key=key, value=value))
    await db.commit()
