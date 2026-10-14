# Backend · FastAPI 后端

## 目录结构与职责

```
app/
├── main.py              # 应用入口：CORS、路由挂载、/uploads 静态服务、启动初始化
├── core/
│   ├── config.py        # 全部配置（读 backend/.env），唯一来源
│   └── security.py      # bcrypt 密码哈希、JWT 签发与校验
├── db/
│   ├── base.py          # ORM 基类 + 时间戳 mixin + 约束命名约定
│   ├── session.py       # async engine、会话工厂、自动建库
│   └── init_db.py       # 首次启动：建表 + 种子数据（幂等）
├── models/              # SQLAlchemy ORM 表定义（users/posts/categories/tags/comments/site_configs）
├── schemas/             # Pydantic DTO：请求/响应模型，前后端数据契约
├── crud/                # 数据访问层：全部 SQL 操作集中在这里
├── api/
│   ├── deps.py          # 依赖注入：get_db、get_current_admin（JWT 校验）
│   └── v1/
│       ├── router.py    # v1 总路由
│       ├── public/      # 前台公开接口（无需登录）
│       └── admin/       # 管理接口（Bearer Token）
└── utils/               # 通用工具（slug 生成等）

uploads/                 # 图片上传目录（运行时生成）
tests/                   # pytest 冒烟测试
```

## 分层约定

- **路由层**只做参数校验、权限校验、调 crud、组装响应，不写 SQL
- **crud 层**只做数据库读写，不 import FastAPI
- **schemas** 是唯一的出入参结构；前端 `types/` 与此一一对应

## 常用命令

```bash
source .venv/bin/activate

# 启动（首次自动建库 xavierblog、建表、写种子数据）
uvicorn app.main:app --reload --port 8000

# 测试
pytest tests/ -v
```

## 表结构变更说明

本项目不使用迁移工具：启动时自动建库建表（`app/db/init_db.py`）。

- **全新环境**（如新服务器）：直接启动即可，自动完成建库、建表、种子数据
- **已有数据的环境**：`create_all` 只建缺失的表，不会给已有表加新字段。
  修改 `app/models/` 后需手动执行 `ALTER TABLE` 补字段，或接受重建表（数据丢失）

## API 一览（/api/v1 前缀）

公开：`GET /posts`、`GET /posts/archive`、`GET /posts/{slug}`、`GET /categories`、
`GET /tags`、`GET /site-info`、`GET /posts/{id}/comments`、`POST /comments`

管理（需 `Authorization: Bearer <token>`）：
`POST /admin/auth/login`、`GET /admin/auth/me`、`PUT /admin/auth/password`、
`GET|POST /admin/posts`、`GET|PUT|DELETE /admin/posts/{id}`、
`GET|POST /admin/categories`、`PUT|DELETE /admin/categories/{id}`、
`GET|POST /admin/tags`、`PUT|DELETE /admin/tags/{id}`、
`GET /admin/comments`、`PUT /admin/comments/{id}/approve|reject`、
`DELETE /admin/comments/{id}`、`POST /admin/comments/{id}/reply`、
`POST|GET|DELETE /admin/uploads`、`GET /admin/dashboard/stats`、
`GET|PUT /admin/site-config`

交互式文档：<http://localhost:8000/docs>
