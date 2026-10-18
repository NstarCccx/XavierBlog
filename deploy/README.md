# XavierBlog Docker 部署

整套服务 5 个容器：

| 容器       | 镜像                    | 作用                                                   |
| -------- | --------------------- | ---------------------------------------------------- |
| nginx    | `nginx:1.27-alpine`   | 统一入口（80 端口）：`/` 博客、`/admin` 管理台、`/api` `/uploads` 后端 |
| frontend | `xavierblog-frontend` | 博客前台静态文件（nginx 托管）                                   |
| admin    | `xavierblog-admin`    | 管理后台静态文件（nginx 托管，`/admin/` 子路径）                     |
| backend  | `xavierblog-backend`  | FastAPI（uvicorn），启动自动建库建表+种子数据                       |
| mysql    | `mysql:8.4`           | 数据库，数据卷 `mysql-data` 持久化                             |

数据卷：`mysql-data`（数据库）、`uploads`（上传图片）、`backend-logs`（后端日志）。
MySQL 不对公网暴露端口，只在容器网络内访问。

## 一、首次准备

### 本地（构建机）

- 安装 Docker Desktop
- 若不用 Docker Desktop，可用 colima（已验证可行）：
  ```bash
  brew install colima docker docker-compose docker-buildx
  mkdir -p ~/.docker/cli-plugins
  ln -sf /opt/homebrew/opt/docker-compose/bin/docker-compose ~/.docker/cli-plugins/docker-compose
  ln -sf /opt/homebrew/opt/docker-buildx/bin/docker-buildx ~/.docker/cli-plugins/docker-buildx
  colima start --cpu 4 --memory 6
  ```
  <br />

### 服务器

- 安装 Docker + compose 插件：`curl -fsSL https://get.docker.com | sh`
- 开放安全组 80 端口

# 二、本地构建推送

```bash
cd deploy
cp .env.example .env
./build-push.sh 
```

`REGISTRY/TAG` 写在 `deploy/.env`，与服务器共用同一份文件最省事
（数据库密码等变量服务器才用，本地可以不填）。

## 三、服务器拉取启动

```bash
# 1. 把 deploy/ 目录传到服务器（或整个仓库 clone 上去）
scp -r deploy user@<服务器IP>:~/xavierblog-deploy

# 2. 服务器上执行（幂等脚本：装 Docker → 自动生成带随机密码的 .env → 登录 → pull → 启动）
cd ~/xavierblog-deploy && ./server-setup.sh
```

`server-setup.sh` 首次运行会：安装 Docker（已装则跳过）→ 从 `.env.example` 生成
`deploy/.env`（REGISTRY 已带缺省值，数据库密码/SECRET\_KEY 随机生成，需要自定义就
`vi .env`）→ 引导 `docker login` 阿里云仓库 → `docker compose pull && up -d`。
之后的日常更新在服务器上也是同一条命令。

启动完成后：

- 博客：`http://<服务器IP>/`
- 管理台：`http://<服务器IP>/admin/`（首次账号 `admin` / `admin123`，**登录后立即改密码**）
- 健康检查：`http://<服务器IP>/api/v1/health`

## 四、日常更新流程

```bash
# 本地：改完代码
cd deploy && ./build-push.sh

# 服务器：
cd XavierBlog/deploy && docker compose pull && docker compose up -d
```

`docker compose up -d` 只会重建镜像变化了的容器，数据库/上传文件不受影响。
（服务器上执行 `./server-setup.sh` 效果相同，它内部就是这两条命令。）

## 五、常用运维命令（服务器 deploy/ 目录下）

```bash
docker compose ps                  # 容器状态
docker compose logs -f backend     # 看后端日志（文件日志在 backend-logs 卷里）
docker compose restart backend     # 重启单个服务

# 数据库备份（导出到宿主机当前目录）
docker compose exec mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" xavierblog' > backup-$(date +%F).sql

# 数据库恢复
docker compose exec -T mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" xavierblog' < backup-2026-10-15.sql

# 彻底清空重来（危险：删库删图片）
docker compose down -v
```

<br />

