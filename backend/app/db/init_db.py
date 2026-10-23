"""首次启动初始化：建库、建表、写入种子数据（幂等，已有数据则跳过）。"""
import logging

from sqlalchemy import func, select, text

from app.core.security import hash_password
from app.crud import crud_site
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine, ensure_database
from app.models import Category, Comment, Post, Tag, User

logger = logging.getLogger(__name__)

WELCOME_POST = """\
## 欢迎来到 XavierBlog

这是系统自动创建的第一篇文章，你可以在管理后台编辑或删除它。

### 你能做什么

- 在**管理后台**（`https://guangxuan.xyz/admin/`）用 `admin / admin123` 登录
- 写新文章、管理分类标签、审核评论、上传图片
- 在**站点设置**里修改站名、简介和关于页

### Markdown 示例

**粗体**、*斜体*、`行内代码`、[链接](https://fastapi.tiangolo.com)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "Hello, XavierBlog!"}
```

> 引用：好记性不如烂笔头。
"""

FASTAPI_POST = """\
## 为什么选 FastAPI

基于 Python 类型标注的现代 Web 框架：自动生成 OpenAPI 文档、原生异步、性能优秀。

### 本项目的后端分层

| 层 | 目录 | 职责 |
| --- | --- | --- |
| 路由 | `app/api/v1` | 参数校验、组装响应 |
| DTO | `app/schemas` | Pydantic 请求/响应模型 |
| 数据访问 | `app/crud` | 全部 SQL 操作 |
| 模型 | `app/models` | SQLAlchemy ORM |

```python
@router.get("", response_model=PageResult[PostBrief])
async def list_posts(page: int = 1, page_size: int = 10):
    items, total = await crud_post.list_posts(db, page=page, page_size=page_size)
    return PageResult(items=items, total=total, page=page, page_size=page_size)
```
"""


async def seed() -> None:
    """写入初始数据（仅当库为空时）。"""
    async with AsyncSessionLocal() as db:
        has_user = (await db.execute(select(func.count()).select_from(User))).scalar_one()
        if has_user:
            logger.info("数据库已有数据，跳过种子初始化")
            return

        db.add(User(
            username="admin",
            hashed_password=hash_password("admin123"),
            nickname="Xavier",
            avatar="",
            role="admin",
        ))

        db.add_all([
            Category(name="技术笔记", slug="tech", description="开发中的实践经验"),
            Category(name="生活随笔", slug="life", description="记录生活点滴"),
        ])

        tags = [Tag(name=t, slug=t.lower()) for t in ["FastAPI", "Vue3", "MySQL", "前端"]]
        db.add_all(tags)
        await db.flush()

        tech, life = (await db.execute(select(Category))).scalars().all()
        fastapi_tag, vue_tag, mysql_tag, fe_tag = tags

        db.add_all([
            Post(
                title="欢迎来到 XavierBlog",
                slug="hello-xavierblog",
                summary="系统自动创建的第一篇文章，介绍这个博客怎么用。",
                content=WELCOME_POST,
                status="published",
                views=42,
                category_id=tech.id,
                tags=[fastapi_tag, vue_tag],
            ),
            Post(
                title="FastAPI 工程化分层实践",
                slug="fastapi-layered-architecture",
                summary="路由、DTO、数据访问、模型四层职责划分。",
                content=FASTAPI_POST,
                status="published",
                views=18,
                category_id=tech.id,
                tags=[fastapi_tag, mysql_tag],
            )
        ])
        await db.flush()

        first_post = (await db.execute(select(Post).limit(1))).scalar_one()
        db.add_all([
            Comment(
                post_id=first_post.id, nickname="访客小张", email="guest@example.com",
                content="博客搭得很漂亮！请问用的什么技术栈？", status="approved",
            ),
            Comment(
                post_id=first_post.id, nickname="Xavier", email="",
                content="FastAPI + Vue3 + MySQL，源码都有分层注释，欢迎交流～",
                status="approved", is_author=True,
            ),
            Comment(
                post_id=first_post.id, nickname="路人甲", email="",
                content="这条评论在等管理员审核。", status="pending",
            ),
        ])

        await db.commit()
        logger.info("种子数据写入完成：管理员 admin/admin123，3 篇示例文章")


async def _ensure_column(conn, table: str, column: str, ddl: str) -> None:
    """幂等加列：create_all 不会给已存在的表补新列。"""
    exists = (await conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() "
        f"AND table_name = '{table}' AND column_name = '{column}'"
    ))).scalar_one()
    if not exists:
        await conn.execute(text(ddl))
        logger.info("已为 %s 表补充 %s 列", table, column)


async def _ensure_fk(conn, table: str, fk_name: str, ddl: str) -> None:
    """幂等加外键约束。"""
    exists = (await conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.table_constraints "
        "WHERE table_schema = DATABASE() AND table_name = :t "
        "AND constraint_name = :n AND constraint_type = 'FOREIGN KEY'"
    ), {"t": table, "n": fk_name})).scalar_one()
    if not exists:
        await conn.execute(text(ddl))
        logger.info("已为 %s 表补充外键 %s", table, fk_name)


async def init_db() -> None:
    """建库 → 建表 → 轻量迁移 → 种子。应用启动时调用。"""
    await ensure_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # create_all 不会给已存在的表加列/外键，这里补齐（幂等）
        await _ensure_column(
            conn, "posts", "is_pinned",
            "ALTER TABLE posts ADD COLUMN is_pinned BOOL NOT NULL DEFAULT 0 COMMENT '是否置顶'",
        )
        await _ensure_column(
            conn, "users", "role",
            "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin' "
            "COMMENT '角色：admin 管理员 / member 注册用户'",
        )
        await _ensure_column(
            conn, "comments", "user_id",
            "ALTER TABLE comments ADD COLUMN user_id INT NULL COMMENT '评论者账号（注销后留空）'",
        )
        await _ensure_fk(
            conn, "comments", "fk_comments_user_id",
            "ALTER TABLE comments ADD CONSTRAINT fk_comments_user_id "
            "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL",
        )
    await seed()
