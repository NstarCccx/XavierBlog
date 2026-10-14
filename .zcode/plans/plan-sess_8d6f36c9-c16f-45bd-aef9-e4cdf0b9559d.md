# XavierBlog 个人博客系统 · 工程规划（v2 · 本地 MySQL 版）

前后台分离的 Monorepo：`backend/`（FastAPI）+ `frontend/`（博客前台）+ `admin/`（管理后台），**直接使用你本地已在运行的 MySQL**，不用 Docker。

```
XavierBlog/
├── backend/              # FastAPI 后端（Python 3.12 虚拟环境）
├── frontend/             # Vue3 + Tailwind 博客前台（dev 端口 5173）
├── admin/                # Vue3 + Element Plus 管理后台（dev 端口 5174）
├── .gitignore
└── README.md             # 总览 + 启动指南
```

## 数据库

- 直连本地 MySQL `localhost:3306`（已确认 mysqld 在运行），root 账号，密码只写 `backend/.env`（.gitignore 排除，另提供 `.env.example`）
- 连接串：`mysql+aiomysql://root:密码@localhost:3306/xavierblog`
- 后端启动时自动执行 `CREATE DATABASE IF NOT EXISTS xavierblog`（utf8mb4），无需手动建库
- 表结构由 SQLAlchemy 建表 + Alembic 管理后续迁移

## 一、后端 backend/ — FastAPI + SQLAlchemy 2.0 (async) + aiomysql + Alembic

分层职责（各层只做自己的事，方便维护测试）：

| 层 | 目录 | 职责 |
|---|---|---|
| 路由层 | `app/api/v1/` | 参数校验、调 crud、返回响应，不写 SQL |
| DTO 层 | `app/schemas/` | Pydantic 请求/响应模型 |
| 数据访问层 | `app/crud/` | 全部数据库操作集中于此 |
| 模型层 | `app/models/` | SQLAlchemy ORM 表定义 |
| 基础设施 | `app/core/` `app/db/` | 配置(.env)、JWT/bcrypt、会话、种子数据 |
| 工具 | `app/utils/` | slug 生成等通用函数 |

```
backend/
├── app/
│   ├── main.py                 # 入口：CORS、/api/v1 路由挂载、uploads 静态服务
│   ├── core/
│   │   ├── config.py           # pydantic-settings 读 .env（数据库/密钥/CORS）
│   │   └── security.py         # JWT 签发校验 + bcrypt 密码哈希
│   ├── db/
│   │   ├── session.py          # async engine + AsyncSessionLocal + 自动建库
│   │   ├── base.py             # DeclarativeBase + id/created_at/updated_at mixin
│   │   └── init_db.py          # 建表 + 种子数据（管理员 admin/admin123、示例分类/标签/3篇文章）
│   ├── models/                 # user / category / tag / post / comment / site_config
│   ├── schemas/                # auth / post / category / tag / comment / common(分页)
│   ├── crud/                   # 对应 6 个模块的数据访问
│   ├── api/
│   │   ├── deps.py             # get_db、get_current_admin 依赖注入
│   │   └── v1/
│   │       ├── public/         # 前台公开接口：posts(列表/详情/归档)、categories、tags、comments(发表)、site
│   │       └── admin/          # 需 JWT：auth(登录/改密)、posts、categories、tags、comments(审核/回复/删除)、uploads(图片上传)、dashboard(统计)、site(设置)
│   └── utils/
├── uploads/                    # 图片上传存储目录（Static Files 对外服务）
├── alembic/                    # 数据库版本迁移
├── tests/test_api.py           # 冒烟测试：健康检查 + 登录
├── requirements.txt
└── .env.example
```

**数据模型（6 表）**：
- `users`：管理员（username、hashed_password、nickname、avatar）
- `categories`：分类（name、slug、description）
- `tags` + `post_tags` 关联表：标签与文章多对多
- `posts`：文章（title、slug、summary、Markdown content、cover、status 草稿/发布、views、category_id 外键）
- `comments`：评论（post_id、parent_id 二级回复、nickname、email、content、status 待审/通过、is_author 博主回复标记）
- `site_configs`：键值对存站点设置（站名、简介、关于页、页脚）

## 二、前台 frontend/ — Vue3 + TypeScript + Vite + Tailwind CSS + Pinia

```
frontend/src/
├── api/          # http.ts(axios 实例+错误处理) + posts/categories/tags/comments/site.ts
├── components/   # layout/(AppHeader,AppFooter) post/(PostCard) common/(Pagination,Empty)
├── composables/  # usePagination 等
├── router/       # 6 个路由
├── stores/       # site.ts（站点信息）
├── types/        # 与后端 schema 一一对应的 TS 类型
├── utils/
└── views/
    ├── HomeView.vue         # 首页：文章分页列表
    ├── PostDetailView.vue   # markdown-it+highlight.js 渲染、自动目录、代码高亮、评论区
    ├── CategoryListView.vue # 按分类浏览
    ├── TagListView.vue      # 按标签浏览
    ├── ArchiveView.vue      # 按年月时间线归档
    └── AboutView.vue        # 关于页（读站点设置）
```

Vite dev 代理 `/api → localhost:8000`，无需处理跨域。

## 三、管理后台 admin/ — Vue3 + TypeScript + Element Plus + Pinia + md-editor-v3

```
admin/src/
├── api/            # axios：请求自动带 Bearer token、401 统一跳登录
├── layouts/AdminLayout.vue   # 经典侧边栏+顶栏布局
├── router/         # 路由守卫：无 token 重定向 /login
├── stores/auth.ts
└── views/
    ├── LoginView.vue        # 登录
    ├── DashboardView.vue    # 统计卡片（文章/评论/总浏览量）
    ├── post/PostList.vue + PostEdit.vue   # 列表(搜索/筛选/分页) + md-editor-v3 编辑（草稿/发布/封面/分类标签）
    ├── CategoryManage.vue / TagManage.vue # 表格 CRUD
    ├── CommentManage.vue    # 待审列表、通过/拒绝、博主回复、删除
    ├── UploadManage.vue     # 图片库（上传/复制链接/删除）
    └── SettingsView.vue     # 站点信息、关于页编辑、修改密码
```

## 实现顺序

1. **根目录**：.gitignore、README
2. **后端**：骨架+配置 → models/schemas/crud → init_db 自动建库建表+种子 → public API → admin API → Alembic 迁移 → 冒烟测试
3. **前台**：Vite+TS+Tailwind 脚手架 → 布局 → 6 个页面 → Markdown 渲染+评论联调
4. **后台**：Vite+TS+Element Plus 脚手架 → 登录+布局+守卫 → 各管理页面
5. **联调验证**：后端启动（自动建 xavierblog 库）→ curl 验证公开/管理接口 → 前台后台页面走通（登录、发文、前台展示、评论审核全流程）

## 说明

- 初始管理员：`admin / admin123`（登录后可在设置页修改）
- MySQL root 密码：实现时我会先写 `.env` 占位符并**问你要一次密码**（用于跑通建库初始化），你也可以自己填 `backend/.env` 后告诉我继续
- Python 用 Homebrew `python3.12` 建 venv；驱动用 aiomysql（纯 Python，ARM Mac 无编译问题）