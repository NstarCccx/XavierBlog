set -euo pipefail
cd "$(dirname "$0")"

# ---------- 1. Docker ----------
if ! command -v docker >/dev/null 2>&1; then
  echo "📦 未安装 Docker，开始安装..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi
docker compose version >/dev/null 2>&1 || {
  echo "❌ 缺少 docker compose 插件（get.docker.com 安装脚本自带，请检查安装方式）" >&2
  exit 1
}

# ---------- 2. .env（缺失则从模板生成；无论来源，空字段一律补齐） ----------
# scp 整个目录时会把本地的 .env（密码留空）一起带上来，所以不能只按文件存在性判断
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "✅ 已从模板生成 deploy/.env"
fi

# 交互式终端下逐项让用户输入（回车=默认值）；管道/CI 等非交互环境自动采用默认值
INTERACTIVE=0
if [[ -t 0 ]]; then INTERACTIVE=1; fi

_ask_value() { # $1=提示文案 $2=默认值 $3=是否在提示中显示默认值(1/0，密码类传 0)
  local input=""
  if [[ "$INTERACTIVE" == "1" ]]; then
    if [[ "${3:-1}" == "1" ]]; then
      read -r -p "$1 [回车=$2]: " input || input=""
    else
      read -r -p "$1 [回车=自动生成]: " input || input=""
    fi
  fi
  printf '%s' "${input:-$2}"
}

_env_fill() { # $1=键 $2=提示文案 $3=默认值 $4=是否显示默认值；仅当键不存在或值为空时写入
  local key="$1" value
  [[ -n "$(awk -F= -v k="$1" '$1==k{sub(/^[^=]*=/,""); print; exit}' .env)" ]] && return
  value="$(_ask_value "$2" "$3" "${4:-1}")"
  if grep -q "^$1=" .env; then
    sed -i.bak "s|^$1=.*|$1=$value|" .env
  else
    printf '%s=%s\n' "$1" "$value" >> .env
  fi
  rm -f .env.bak
}

echo "👇 配置 deploy/.env：已填过的项自动跳过，直接回车采用方括号里的默认值"
_env_fill REGISTRY "镜像仓库地址（REGISTRY）" "crpi-mj7u15y6i9cfm1vy.cn-guangzhou.personal.cr.aliyuncs.com/xavierblog"
_env_fill TAG "镜像标签（TAG）" "latest"
_env_fill HTTP_PORT "HTTP 对外端口" "80"
_env_fill HTTPS_PORT "HTTPS 对外端口" "443"
_env_fill MYSQL_ROOT_PASSWORD "MySQL root 密码" "$(openssl rand -hex 16)" 0
_env_fill DB_PASSWORD "应用数据库密码（DB_PASSWORD）" "$(openssl rand -hex 16)" 0
_env_fill SECRET_KEY "JWT 签名密钥（SECRET_KEY）" "$(openssl rand -hex 32)" 0
echo "✅ deploy/.env 校验完毕（已填项保留原值，其余按输入/默认值写入，可再 vi .env 调整）"

REGISTRY_HOST="$(awk -F= -v k=REGISTRY '$1==k{sub(/^[^=]*=/,""); print; exit}' .env | cut -d/ -f1)"
: "${REGISTRY_HOST:?deploy/.env 中未设置 REGISTRY}"

# ---------- 3. 镜像仓库登录 ----------
if grep -q "\"${REGISTRY_HOST}\"" ~/.docker/config.json 2>/dev/null; then
  echo "✅ 已登录 ${REGISTRY_HOST}"
else
  echo "🔐 首次需要登录镜像仓库（用户名/密码见 ACR 控制台「访问凭证」）"
  docker login "${REGISTRY_HOST}"
fi

# ---------- 4. 拉取并启动 ----------
echo "⬇️  拉取镜像..."
docker compose pull
echo "🚀 启动服务..."
docker compose up -d
docker compose ps

IP="$(curl -s -m 5 ifconfig.me 2>/dev/null || echo '<服务器IP>')"
PORT="$(awk -F= -v k=HTTP_PORT '$1==k{print $2; exit}' .env)"
PORT="${PORT:-80}"
[[ "$PORT" == "80" ]] || PORT_PART=":${PORT}"
echo
echo "🎉 部署完成："
echo "   博客   http://${IP}${PORT_PART}/"
echo "   管理台 http://${IP}${PORT_PART}/admin/  （首次账号 admin/admin123，登录后立即改密码）"
echo "   健康检查 http://${IP}${PORT_PART}/api/v1/health"
