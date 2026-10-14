# XavierBlog · 个人博客系统

一个现代化的前后端分离个人博客系统，支持 Markdown 写作、评论管理、图片上传和完整的站点配置。

## 特性

- **Markdown 写作** — 支持代码高亮、目录提取、封面图，草稿/发布状态管理
- **分类与标签** — 文章多对多归类，灵活的分类体系
- **评论系统** — 游客留言（默认待审核）、博主回复、后台审核管理
- **管理后台** — 仪表盘统计、文章/分类/标签/评论管理、图片库、站点设置
- **前台展示** — 首页列表、文章详情（代码高亮 + 侧边目录）、分类/标签浏览、时间线归档、关于页
- **自动初始化** — 首次启动自动建库建表、写入种子数据，无需手动配置数据库

## 技术栈

### 后端
- **FastAPI** — 现代异步 Web 框架，自动生成 OpenAPI 文档
- **SQLAlchemy 2.0** — 异步 ORM，类型安全的数据库操作
- **MySQL 8.x** — 主数据库（utf8mb4 字符集）
- **Pydantic** — 请求/响应数据校验
- **JWT** — 无状态认证

### 前台
- **Vue 3** — 组合式 API + `<script setup>`
- **TypeScript** — 类型安全
- **Vite** — 极速开发体验
- **Tailwind CSS v4** — 原子化样式
- **Pinia** — 状态管理
- **markdown-it** — Markdown 渲染 + highlight.js 代码高亮

### 管理后台
- **Vue 3 + TypeScript + Vite**
- **Element Plus** — UI 组件库
- **md-editor-v3** — Markdown 编辑器
- **ECharts** — 数据可视化仪表盘
- **Axios** — HTTP 请求

## 架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  博客前台   │      │  管理后台   │      │   后端 API  │
│  :5173      │      │  :5174      │      │   :8000     │
│  Vue3       │      │  Vue3       │      │  FastAPI    │
│  Tailwind   │      │  Element+   │      │  SQLAlchemy │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    MySQL      │
                    │  xavierblog   │
                    └───────────────┘
```

**后端分层**：路由（参数校验）→ DTO（Pydantic）→ CRUD（数据访问）→ ORM（模型）

## 快速启动

### 前置要求

- Python 3.12+
- Node.js 18+
- MySQL 5.7+ 或 8.x（本地运行，默认 `localhost:3306`）

### 1. 启动后端

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，至少修改 DB_PASSWORD 和 SECRET_KEY

# 启动（首次自动建库建表 + 种子数据）
uvicorn app.main:app --reload --port 8000
```

首次启动会自动：
- 创建 `xavierblog` 数据库（utf8mb4）
- 创建所有表（users、posts、categories、tags、comments、site_configs）
- 写入初始数据：管理员账号 `admin / admin123`、3 篇示例文章、2 个分类、4 个标签

访问 API 文档：<http://localhost:8000/docs>

### 2. 启动博客前台

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### 3. 启动管理后台

```bash
cd admin
npm install
npm run dev        # http://localhost:5174
```

用 `admin / admin123` 登录管理后台，建议首次登录后修改密码。

## 项目结构

```
XavierBlog/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # 应用入口，启动时自动初始化数据库
│   │   ├── core/        # 配置、安全（JWT、密码哈希）
│   │   ├── db/          # 数据库会话、建库建表、种子数据
│   │   ├── models/      # ORM 模型（6 张表）
│   │   ├── schemas/     # Pydantic DTO
│   │   ├── crud/        # 数据访问层
│   │   └── api/v1/      # 路由（public + admin）
│   ├── uploads/         # 图片上传目录（运行时生成）
│   ├── .env.example     # 环境变量模板
│   └── requirements.txt
│
├── frontend/            # 博客前台
│   └── src/
│       ├── api/         # 接口封装
│       ├── components/  # 组件（layout、post、comment、common）
│       ├── views/       # 页面（首页、详情、归档、关于等）
│       ├── stores/      # Pinia 状态
│       └── types/       # TypeScript 类型
│
└── admin/               # 管理后台
    └── src/
        ├── api/         # 接口封装（自动带 token）
        ├── views/       # 页面（仪表盘、文章、分类、标签、评论、图片、设置）
        ├── stores/      # 认证状态
        └── types/       # TypeScript 类型
```

## 数据库设计

6 张核心表：

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 管理员 | username, hashed_password, nickname |
| `posts` | 文章 | title, slug, content, status, views, category_id |
| `categories` | 分类 | name, slug, description |
| `tags` | 标签 | name, slug |
| `post_tags` | 文章-标签关联 | post_id, tag_id |
| `comments` | 评论 | post_id, nickname, content, status, is_author |
| `site_configs` | 站点配置 | key, value（单行存储） |

所有业务表包含 `created_at`、`updated_at` 时间戳字段。

## API 概览

### 公开接口（无需认证）

- `GET /api/v1/posts` — 文章列表（分页）
- `GET /api/v1/posts/{slug}` — 文章详情
- `GET /api/v1/posts/archive` — 归档时间线
- `GET /api/v1/categories` — 分类列表
- `GET /api/v1/tags` — 标签列表
- `GET /api/v1/site-info` — 站点信息
- `GET /api/v1/posts/{id}/comments` — 评论列表
- `POST /api/v1/comments` — 提交评论

### 管理接口（Bearer Token）

- `POST /api/v1/admin/auth/login` — 登录
- `GET /api/v1/admin/auth/me` — 当前用户
- `GET/POST /api/v1/admin/posts` — 文章管理
- `GET/POST /api/v1/admin/categories` — 分类管理
- `GET/POST /api/v1/admin/tags` — 标签管理
- `GET /api/v1/admin/comments` — 评论审核
- `POST/GET/DELETE /api/v1/admin/uploads` — 图片上传
- `GET/PUT /api/v1/admin/site-config` — 站点设置
- `GET /api/v1/admin/dashboard/stats` — 仪表盘统计

完整文档：启动后端后访问 <http://localhost:8000/docs>

## 部署到服务器

### 1. 准备 MySQL

```bash
# 创建数据库用户（建议非 root）
mysql -u root -p -e "CREATE USER 'xavier'@'localhost' IDENTIFIED BY '强密码';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON *.* TO 'xavier'@'localhost';"
```

### 2. 部署后端

```bash
cd /path/to/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
vim .env  # 修改 DB_PASSWORD、SECRET_KEY、CORS_ORIGINS

# 生产环境启动
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

首次启动自动建库建表。

### 3. 部署前端

```bash
cd frontend
npm install
npm run build    # 产物在 dist/

# 用 nginx 托管 dist/，反向代理 /api 到后端
```

管理后台同理，build 后托管。

### 4. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 博客前台
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台
    location /admin {
        alias /path/to/admin/dist;
        try_files $uri $uri/ /admin/index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 图片上传
    location /uploads {
        alias /path/to/backend/uploads;
    }
}
```

## 开发说明

### 表结构变更

本项目不使用迁移工具（如 Alembic），启动时自动建库建表。

- **全新环境**：直接启动，自动完成初始化
- **已有数据**：`create_all` 只建缺失的表，不会给已有表加新字段。修改模型后需手动 `ALTER TABLE` 或重建表

### 环境变量

后端配置集中在 `backend/.env`，所有配置项见 `.env.example`：

- `DB_*` — 数据库连接
- `SECRET_KEY` — JWT 签名密钥（生产环境必须修改）
- `CORS_ORIGINS` — 跨域白名单
- `DEBUG` — 调试模式

## 截图

> 待补充

## 许可证

MIT
