# XavierBlog · 个人博客系统

（❤️  🩸  莱  绰  慧  🥣明   🔁 - 炒肝）一个现代化的前后端分离个人博客系统，支持 Markdown 写作、评论管理、图片上传和完整的站点配置

| <br /> | <br />                                    |
| ------ | ----------------------------------------- |
| 线上地址   | <https://guangxuan.xyz>                   |
| 源码仓库   | <https://github.com/NstarCccx/XavierBlog> |

## 特性

- **Markdown 写作** — 支持代码高亮、目录提取、封面图，草稿/发布状态管理、文章置顶
- **分类与标签** — 文章多对多归类，灵活的分类体系
- **评论系统** — 游客留言（默认待审核）、博主回复、后台审核管理
- **管理后台** — 仪表盘统计、文章/分类/标签/评论管理、图片库、站点设置
- **前台展示** — 首页列表、文章详情（代码高亮 + 侧边目录）、分类/标签浏览、时间线归档、关于页
- **自动初始化** — 首次启动自动建库建表、写入种子数据，无需手动配置数据库
- **站点备案信息** — ICP 备案号链接工信部查询，公安备案号带图标展示，均可在后台编辑
- **容器化部署** — 5 个容器（nginx 网关 + 前后台 + FastAPI + MySQL），一条命令上线，自动续签 HTTPS 证书

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

### 部署

- **Docker + Docker Compose** — 5 容器编排（nginx 网关 / 前后台 / FastAPI / MySQL）
- **nginx** — 统一入口，反代 `/api`、`/uploads`，托管前后台静态资源
- **Let's Encrypt** — 免费证书，90 天有效期，自动续期

## 架构

### 本地开发

```
┌─────────────┐      ┌─────────────┐      ┌───────────────┐
│  博客前台   │      │  管理后台   │      │    后端 API   │
│  :8082      │      │  :8083      │      │    :8000      │
│  Vue3       │      │  Vue3       │      │   FastAPI     │
│  Tailwind   │      │  Element+   │      │  SQLAlchemy   │
└──────┬──────┘      └──────┬──────┘      └───────┬───────┘
       │   Vite dev proxy   │                      │
       └────────────────────┴──────────────────────┘
                            │  /api/v1
                            ▼
                    ┌───────────────┐
                    │    MySQL      │
                    │  xavierblog   │
                    └───────────────┘
```

### 生产部署（Docker Compose）

```
                    ┌────────────────────┐
                    │  nginx 网关 :80/:443│
                    │  /  → frontend      │
                    │  /admin/ → admin    │
                    │  /api/ /uploads/    │
                    │         → backend   │
                    └─────────┬──────────┘
                              │ 容器内网
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   frontend    │     │     admin     │     │    backend    │
│  nginx 静态   │     │  nginx 静态   │     │   FastAPI     │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                     │
                                             ┌───────▼───────┐
                                             │    MySQL 8.4  │
                                             │  mysql-data 卷 │
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
- 创建所有表（users、posts、categories、tags、post\_tags、comments、site\_configs）

访问 API 文档：<http://localhost:8000/docs>

### 2. 启动博客前台

```bash
cd frontend
npm install
npm run dev        # http://localhost:8082
```

### 3. 启动管理后台

```bash
cd admin
npm install
npm run dev        # http://localhost:8083
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
│   │   ├── models/      # ORM 模型（7 张表）
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
├── admin/               # 管理后台
│   └── src/
│       ├── api/         # 接口封装（自动带 token）
│       ├── views/       # 页面（仪表盘、文章、分类、标签、评论、图片、设置）
│       ├── stores/      # 认证状态
│       └── types/       # TypeScript 类型
│
└── deploy/              # Docker 部署
    ├── docker-compose.yml   # 5 容器编排
    ├── build-push.sh        # 构建并推送镜像到 ACR
    ├── server-setup.sh      # 服务器一键部署
    ├── enable-https.sh      # 签发证书 + 切换 HTTPS + 自动续期
    ├── nginx/               # 网关配置（HTTP / HTTPS 两套）
    ├── certbot/             # 证书与 ACME 验证目录
    └── .env.example         # 部署环境变量模板
```

## 数据库设计

7 张表：

| 表名             | 说明      | 关键字段                                                          |
| -------------- | ------- | ------------------------------------------------------------- |
| `users`        | 管理员     | username, hashed\_password, nickname                          |
| `posts`        | 文章      | title, slug, content, status, views, is\_pinned, category\_id |
| `categories`   | 分类      | name, slug, description                                       |
| `tags`         | 标签      | name, slug                                                    |
| `post_tags`    | 文章-标签关联 | post\_id, tag\_id                                             |
| `comments`     | 评论      | post\_id, nickname, content, status, is\_author               |
| `site_configs` | 站点配置    | key, value（键值表，每行一项配置）                                        |

`users`、`posts`、`categories`、`tags`、`comments` 含 `created_at`、`updated_at` 时间戳字段；`site_configs` 为纯键值表，无时间戳。

## API 概览

### 公开接口（无需认证）

- `GET /api/v1/posts` — 已发布文章分页
- `GET /api/v1/posts/{slug}` — 文章详情（浏览量 +1）
- `GET /api/v1/posts/archive` — 归档时间线
- `GET /api/v1/categories` — 分类列表
- `GET /api/v1/tags` — 标签列表
- `GET /api/v1/site-info` — 站点信息（含备案号）
- `GET /api/v1/posts/{id}/comments` — 已审核评论（树形）
- `POST /api/v1/comments` — 提交评论（默认待审核）
- `GET /api/v1/health` — 健康检查

### 管理接口（Bearer Token）

- `POST /api/v1/admin/auth/login` — 登录获取 Token
- `GET /api/v1/admin/auth/me` — 当前管理员信息
- `PUT /api/v1/admin/auth/password` — 修改密码
- `GET/POST /api/v1/admin/posts` — 文章管理（含草稿、置顶）
- `GET/PUT/DELETE /api/v1/admin/posts/{id}` — 文章详情 / 更新 / 删除
- `GET/POST /api/v1/admin/categories` — 分类管理
- `PUT/DELETE /api/v1/admin/categories/{id}` — 更新 / 删除分类
- `GET/POST /api/v1/admin/tags` — 标签管理
- `PUT/DELETE /api/v1/admin/tags/{id}` — 更新 / 删除标签
- `GET /api/v1/admin/comments` — 评论分页
- `PUT /api/v1/admin/comments/{id}/approve` — 通过评论
- `PUT /api/v1/admin/comments/{id}/reject` — 退回待审核
- `POST /api/v1/admin/comments/{id}/reply` — 以博主身份回复
- `DELETE /api/v1/admin/comments/{id}` — 删除评论
- `POST/GET/DELETE /api/v1/admin/uploads` — 图片上传 / 图库列表 / 删除
- `GET/PUT /api/v1/admin/site-config` — 站点设置（含备案信息）
- `GET /api/v1/admin/dashboard/stats` — 仪表盘统计

完整文档：启动后端后访问 <http://localhost:8000/docs>

## 部署到服务器

完整部署手册见 [`deploy/README.md`](deploy/README.md)，以下为概要。

### 部署结构

| 容器       | 镜像                    | 作用                                                     |
| -------- | --------------------- | ------------------------------------------------------ |
| nginx    | `nginx:1.27-alpine`   | 统一入口（80/443）：`/` 博客、`/admin/` 管理台、`/api` `/uploads` 后端 |
| frontend | `xavierblog-frontend` | 博客前台静态文件（nginx 托管）                                     |
| admin    | `xavierblog-admin`    | 管理后台静态文件（nginx 托管，`/admin/` 子路径）                       |
| backend  | `xavierblog-backend`  | FastAPI（uvicorn），启动自动建库建表 + 种子数据                       |
| mysql    | `mysql:8.4`           | 数据库，数据卷 `mysql-data` 持久化                               |

数据卷：`mysql-data`（数据库）、`uploads`（上传图片）、`backend-logs`（后端日志）。

### 1. 服务器前置准备

```bash
# 安装 Docker + compose 插件
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
```

- 云安全组放行 80 / 443 端口
- DNS 解析：`guangxuan.xyz` 与 `www.guangxuan.xyz` 的 A 记录指向服务器公网 IP

### 2. 上传部署文件并启动

```bash
# 把 deploy/ 目录传到服务器
scp -r deploy user@<服务器IP>:~/xavierblog/

# 一键脚本：装 Docker → 生成 .env（随机密码）→ 登录镜像仓库 → pull → up -d
cd ~/xavierblog/deploy && ./server-setup.sh
```

首次运行会提示输入镜像仓库账号密码（阿里云 ACR 控制台「访问凭证」）；数据库密码留空则自动随机生成。

### 3. 启用 HTTPS

```bash
cd ~/xavierblog/deploy
./enable-https.sh your-email@example.com
```

自动申请 Let's Encrypt 证书、网关切到 443、装每天两次的自动续期 crontab。邮箱仅用于接收到期提醒，续签全自动。

### 4. 日常更新

```bash
# 本地：改完代码重新构建推送
cd deploy && ./build-push.sh

# 服务器：
cd ~/xavierblog/deploy && docker compose pull && docker compose up -d
```

数据库卷与上传文件卷不受影响。

### 数据库远程连接（Navicat）

容器已启用 `mysql_native_password` 认证插件并放开 root 远程登录，Navicat 直接连接：

| 项   | 值                                      |
| --- | -------------------------------------- |
| 主机  | 服务器公网 IP                               |
| 端口  | `3306`                                 |
| 用户名 | `root` 或应用账号 `xavierblog`              |
| 密码  | `deploy/.env` 中的 `MYSQL_ROOT_PASSWORD` |
| 数据库 | `xavierblog`                           |
| 字符集 | `utf8mb4` / `utf8mb4_unicode_ci`       |

更安全的做法是把 `DB_PUBLIC_HOST` 改成 `127.0.0.1`，再用 SSH 隧道连：`ssh -L 3306:127.0.0.1:3306 user@<服务器IP>`。

## 许可证

MIT — Copyright (c) 2026 GuangXuan Chen
