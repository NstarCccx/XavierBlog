# XavierBlog · 个人博客系统

（❤️  🩸  莱  绰  慧  🥣明   🔁 - 炒肝）一个现代化的前后端分离个人博客系统，支持 Markdown 写作、用户注册与登录评论、图片上传和完整的站点配置

| <br /> | <br />                                    |
| ------ | ----------------------------------------- |
| 线上地址   | <https://guangxuan.xyz>                   |
| 源码仓库   | <https://github.com/NstarCccx/XavierBlog> |

## 特性

- **Markdown 写作** — 支持代码高亮、目录提取、封面图，草稿/发布状态管理、文章置顶
- **用户账号** — 前台注册/登录（用户名 + 昵称 + 密码），仅登录用户可评论；管理员与注册用户同表异角色（`role`），权限互不越界
- **分类与标签** — 文章多对多归类，灵活的分类体系
- **评论系统** — 登录用户评论即时展示、博主回复自动带徽章、后台审核管理
- **管理后台** — 仪表盘统计、文章/分类/标签/评论管理、图片库、站点设置
- **前台展示** — 首页列表、文章详情（代码高亮 + 侧边目录）、分类/标签浏览、时间线归档、关于页；中英文双语界面
- **自动初始化** — 首次启动自动建库建表、写入种子数据；版本升级新增字段时启动自动补列补外键，无需手工迁移数据库
- **站点备案信息** — ICP 备案号链接工信部查询，公安备案号带图标展示，均可在后台编辑
- **容器化部署** — 5 个容器（nginx 网关 + 前后台 + FastAPI + MySQL），一条命令上线，自动续签 HTTPS 证书

## 技术栈

### 后端

- **FastAPI** — 现代异步 Web 框架，自动生成 OpenAPI 文档
- **SQLAlchemy 2.0** — 异步 ORM，类型安全的数据库操作
- **MySQL 8.x** — 主数据库（utf8mb4 字符集）
- **Pydantic** — 请求/响应数据校验
- **JWT** — 无状态认证，前台用户与后台管理员共用签发体系，按 `role` 隔离权限

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

前台账号在页面顶栏「登录 / 注册」创建（用户名 + 昵称 + 密码），登录后才能发表评论。

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
│       ├── api/         # 接口封装（含 token 存取与自动携带）
│       ├── components/  # 组件（layout、post、comment、auth、common）
│       ├── views/       # 页面（首页、详情、归档、关于等）
│       ├── stores/      # Pinia 状态（站点配置、登录态）
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
| `users`        | 用户      | username, hashed\_password, nickname, role（admin 管理员 / member 注册用户） |
| `posts`        | 文章      | title, slug, content, status, views, is\_pinned, category\_id |
| `categories`   | 分类      | name, slug, description                                       |
| `tags`         | 标签      | name, slug                                                    |
| `post_tags`    | 文章-标签关联 | post\_id, tag\_id                                             |
| `comments`     | 评论      | post\_id, user\_id, nickname（快照）, content, status, is\_author |
| `site_configs` | 站点配置    | key, value（键值表，每行一项配置）                                        |

`users`、`posts`、`categories`、`tags`、`comments` 含 `created_at`、`updated_at` 时间戳字段；`site_configs` 为纯键值表，无时间戳。

三点设计说明：

- **账号与权限**：`users` 单表双角色，`role=admin` 是博主（可登录管理后台），`role=member` 是前台注册用户（只能评论）；两边登录接口都会校验角色，普通用户拿不到后台 Token。
- **评论快照**：评论发表时把昵称固化进 `comments.nickname`，账号关联 `user_id` 在外键上 `ON DELETE SET NULL`——注销账号不影响历史评论展示。
- **免手工迁移**：`init_db()` 启动时用 `information_schema` 判断并幂等 `ALTER TABLE` 补新列/外键，老库拉到新镜像直接升级。

## API 概览

### 公开接口（无需登录）

- `GET /api/v1/posts` — 已发布文章分页
- `GET /api/v1/posts/{slug}` — 文章详情（浏览量 +1）
- `GET /api/v1/posts/archive` — 归档时间线
- `GET /api/v1/categories` — 分类列表
- `GET /api/v1/tags` — 标签列表
- `GET /api/v1/site-info` — 站点信息（含备案号）
- `GET /api/v1/posts/{id}/comments` — 已通过审核的评论（树形）
- `POST /api/v1/auth/register` — 注册用户，成功直接返回 Token
- `POST /api/v1/auth/login` — 前台登录，返回 Token
- `GET /api/v1/health` — 健康检查

### 前台接口（需 Bearer Token）

- `GET /api/v1/auth/me` — 当前登录用户
- `POST /api/v1/comments` — 发表评论（昵称取账号快照，博主账号自动带徽章，即时展示）

### 管理接口（需管理员 Token，普通用户 403）

- `POST /api/v1/admin/auth/login` — 管理端登录（仅 `role=admin`）
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
| backend  | `xavierblog-backend`  | FastAPI（uvicorn），启动自动建库建表 + 种子数据 + 新字段迁移          |
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

### 2. 上传部署文件并启动（仅首次）

```bash
# 把 deploy/ 目录传到服务器
scp -r deploy user@<服务器IP>:~/xavierblog/

# 一键脚本：装 Docker → 生成 .env（随机密码）→ 登录镜像仓库 → pull → up -d
cd ~/xavierblog/deploy && ./server-setup.sh
```

首次运行会提示输入镜像仓库账号密码（阿里云 ACR 控制台「访问凭证」）；数据库密码留空则自动随机生成。

> 传目录只在首次部署做一次。之后代码都走镜像，**不要再 `scp -r deploy/` 覆盖服务器**——
> 那会用仓库里的 HTTP 版 `nginx/gateway.conf` 盖掉已切换的 SSL 配置（443 监听直接消失），
> 也可能重置服务器上的 `.env` 数据库密码。

### 3. 启用 HTTPS

```bash
cd ~/xavierblog/deploy
./enable-https.sh your-email@example.com
```

自动申请 Let's Encrypt 证书、网关切到 443、装每天两次的自动续期 crontab。邮箱仅用于接收到期提醒，续签全自动。

### 4. 日常更新

```bash
# 本地：改完代码重新构建推送（自动拉起 colima，构建 linux/amd64 三镜像并推 ACR）
cd deploy && ./build-push.sh

# 服务器：只跑这两条，不需要重传代码
cd ~/xavierblog/deploy && docker compose pull && docker compose up -d
```

`up -d` 只重建镜像变了的容器，数据库卷、上传文件卷与 `.env` 均不受影响；后端容器启动时会自动补齐本版本新增的数据库列/外键。

服务器上同样**不要 `git pull` 整个仓库来更新**：`nginx/gateway.conf` 是被版本管理的文件，
`enable-https.sh` 已在服务器上把它改成了 SSL 版，pull 会冲突或打回 HTTP 模式。

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
