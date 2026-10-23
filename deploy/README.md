# XavierBlog Docker 部署

整套服务 5 个容器：

| 容器       | 镜像                    | 作用                                                   |
| -------- | --------------------- | ---------------------------------------------------- |
| nginx    | `nginx:1.27-alpine`   | 统一入口（80 / 443）：`/` 博客、`/admin` 管理台、`/api` `/uploads` 后端 |
| frontend | `xavierblog-frontend` | 博客前台静态文件（nginx 托管）                                   |
| admin    | `xavierblog-admin`    | 管理后台静态文件（nginx 托管，`/admin/` 子路径）                     |
| backend  | `xavierblog-backend`  | FastAPI（uvicorn），启动自动建库建表 + 种子数据 + 新增字段迁移            |
| mysql    | `mysql:8.4`           | 数据库，数据卷 `mysql-data` 持久化                             |

数据卷：`mysql-data`（数据库）、`uploads`（上传图片）、`backend-logs`（后端日志）。
MySQL 默认映射到宿主机 3306 端口（供 Navicat 连接），可通过 `DB_PUBLIC_HOST` 收紧为仅本机。

线上域名：`guangxuan.xyz`（备案号 粤ICP备2026162376号）。

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
- 云安全组放行 80 / 443 端口（443 在启用 HTTPS 后使用）
- DNS 解析：`guangxuan.xyz` 与 `www.guangxuan.xyz` 的 A 记录指向服务器公网 IP

## 二、本地构建推送

```bash
cd deploy
cp .env.example .env
./build-push.sh 
```

`REGISTRY/TAG` 写在 `deploy/.env`，与服务器共用同一份文件最省事
（数据库密码等变量服务器才用，本地可以不填）。

## 三、服务器拉取启动（首次部署）

```bash
# 1. 把 deploy/ 目录传到服务器（仅首次；之后代码都走镜像，别再重传覆盖）
scp -r deploy user@<服务器IP>:~/xavierblog-deploy

# 2. 服务器上执行（幂等脚本：装 Docker → 自动生成带随机密码的 .env → 登录 → pull → 启动）
cd ~/xavierblog-deploy && ./server-setup.sh
```

`server-setup.sh` 首次运行会：安装 Docker（已装则跳过）→ 从 `.env.example` 生成
`deploy/.env`（REGISTRY 已带缺省值，数据库密码/SECRET\_KEY 随机生成，需要自定义就
`vi .env`）→ 引导 `docker login` 阿里云仓库 → `docker compose pull && up -d`。
之后的日常更新在服务器上也是同一条命令。

> ⚠️ 传目录只做这一次。启用过 HTTPS 之后再 `scp -r deploy/` 覆盖，会用仓库里的
> HTTP 版 `nginx/gateway.conf` 盖掉服务器上的 SSL 版（`enable-https.sh` 是就地改写
> 这个文件的），443 监听随之消失；`.env` 里的数据库密码也可能被空值覆盖。

启动完成后：

- 博客：`http://<服务器IP>/`（或 `http://guangxuan.xyz/`）
- 管理台：`http://<服务器IP>/admin/`（首次账号 `admin` / `admin123`，**登录后立即改密码**）
- 健康检查：`http://<服务器IP>/api/v1/health`

## 四、启用 HTTPS（备案后必做）

域名解析生效后，在服务器 `deploy/` 目录执行：

```bash
./enable-https.sh your-email@example.com
```

脚本会自动向 Let's Encrypt 申请 `guangxuan.xyz` 证书、切换网关到 HTTPS、
并安装每天两次的自动续期 crontab。完成后访问 `https://guangxuan.xyz`。

## 五、Navicat 连接数据库

数据库已做兼容处理，直接用 Navicat 连 MySQL 即可：

| 项                    | 值                                        |
| --------------------- | ----------------------------------------- |
| 主机                  | 服务器公网 IP                             |
| 端口                  | `3306`（由 `DB_PUBLIC_PORT` 控制）        |
| 用户名                | `root`（或应用账号 `xavierblog`）         |
| 密码                  | `deploy/.env` 中的 `MYSQL_ROOT_PASSWORD`  |
| 数据库                | `xavierblog`                              |
| 字符集                | `utf8mb4` / `utf8mb4_unicode_ci`          |

密码查看：`cd deploy && grep MYSQL_ROOT_PASSWORD .env`

**Navicat 连接前必须先在云服务器安全组放行 3306 端口**（来源 IP 建议只填自己
办公网的 IP，不要用 `0.0.0.0/0`）。

更安全的做法：把 `deploy/.env` 里的 `DB_PUBLIC_HOST` 改成 `127.0.0.1`，然后本地
建 SSH 隧道再连，端口完全不对公网暴露：

```bash
ssh -L 3306:127.0.0.1:3306 user@服务器IP
# Navicat 里主机填 127.0.0.1，端口 3306
```

> 兼容性说明：容器已启用 `mysql_native_password` 认证插件。Navicat 老版本不识别
> MySQL 8 默认的 `caching_sha2_password`，若握手报 `authentication plugin not loaded`
> 即为该问题，升级 Navicat 或使用当前配置即可。

## 六、日常更新流程

```bash
# 本地：改完代码
cd deploy && ./build-push.sh

# 服务器：
cd XavierBlog/deploy && docker compose pull && docker compose up -d
```

`docker compose up -d` 只会重建镜像变化了的容器，数据库/上传文件不受影响。
（服务器上执行 `./server-setup.sh` 效果相同，它内部就是这两条命令。）

后端版本升级涉及新数据库字段时（如 `users.role`、`comments.user_id`），后端容器启动
会自动幂等补列补外键，**不需要手工执行 SQL**：

```bash
docker compose logs backend | grep 补充   # 看到「已为 users 表补充 role 列」即迁移完成
```

> ⚠️ 更新只走镜像：不要 `scp -r deploy/` 重传、也不要在服务器上 `git pull` 整个仓库。
> `nginx/gateway.conf` 受版本管理且被 `enable-https.sh` 就地改写过，重传或 pull 会把它
> 打回 HTTP 版（443 监听消失）或产生冲突。确实需要改 `docker-compose.yml`、`nginx/*.conf`
> 这类宿主机文件时，只传单文件，且传前先确认不会覆盖服务器上的 SSL 版 `gateway.conf`。

## 七、常用运维命令（服务器 deploy/ 目录下）

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

## 八、常见问题排查

### 443 端口无监听（HTTPS 打不开）

443 是否监听只取决于挂进容器的 `nginx/gateway.conf` 里有没有 443 server 块：
仓库入库的是 HTTP 版，只有 `enable-https.sh` 跑成功才会就地换成 SSL 版。

```bash
cd ~/xavierblog/deploy

grep -n "listen" nginx/gateway.conf          # ① 应出现 listen 443 ssl
docker compose ps nginx                      # ② 状态应为 Up，而不是 Restarting
docker compose logs --tail=30 nginx          # ③ 看是否 cannot load certificate
ls -l certbot/conf/live/guangxuan.xyz/       # ④ 证书文件是否存在
ss -tlnp | grep -E ':80 |:443 '              # ⑤ 宿主机端口映射（docker-proxy）
docker inspect $(docker compose ps -q nginx) --format '{{json .NetworkSettings.Ports}}'  # ⑥ 实际映射
```

| 现象 | 原因 | 处理 |
| ---- | ---- | ---- |
| ① 里没有 `listen 443`，80 正常 | gateway.conf 被打回 HTTP 版（重传过 deploy/ 或 git pull），或 `enable-https.sh` 从未跑成功 | 重跑 `./enable-https.sh 邮箱`（证书已存在时会跳过签发，只切换配置） |
| ② nginx Restarting、③ 报 `cannot load certificate` | 配置里有 443 块但 ④ 证书目录为空：签发失败或换过目录 | 确认 DNS 与 80 端口公网可达后重跑 `./enable-https.sh`；期间可临时用 HTTP 版配置恢复 80 |
| ①⑤ 都正常、外网仍连不上 | 云安全组/防火墙没放行 443 | 控制台放行 443（来源 `0.0.0.0/0`） |
| ⑥ 里没有 `443/tcp` | `.env` 的 `HTTPS_PORT` 被改或 compose 未重建 | 核对 `.env` 后 `docker compose up -d` 重建 nginx |

<br />

