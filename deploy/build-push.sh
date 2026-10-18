set -euo pipefail
cd "$(dirname "$0")/.." # 回到仓库根目录

# Docker 运行时（colima）平时保持关闭省内存，构建时自动拉起
if ! docker info >/dev/null 2>&1; then
  echo "▶️  Docker 运行时未启动，自动启动 colima..."
  colima start
fi

if [[ ! -f deploy/.env ]]; then
  echo "❌ 缺少 deploy/.env，先执行：cp deploy/.env.example deploy/.env 并填写 REGISTRY" >&2
  exit 1
fi

# shellcheck disable=SC1091
# 不用 source <(grep ...)：部分 bash 环境下进程替换 source 会静默拿到空内容
_env_val() { awk -F= -v k="$1" '$1==k{sub(/^[^=]*=/,""); print; exit}' deploy/.env; }
REGISTRY="$(_env_val REGISTRY)"
TAG="${1:-$(_env_val TAG)}"
: "${REGISTRY:?deploy/.env 中未设置 REGISTRY}"
TAG="${TAG:-latest}"

REGISTRY_HOST="${REGISTRY%%/*}"
# 已登录则跳过（避免非交互环境卡在密码提示）；凭证存于 ~/.docker/config.json
if grep -q "\"${REGISTRY_HOST}\"" ~/.docker/config.json 2>/dev/null; then
  echo "✅ 已登录 ${REGISTRY_HOST}，跳过 login"
else
  echo "🔐 登录 ${REGISTRY_HOST}（用户名/密码见 ACR 控制台「访问凭证」）"
  docker login "${REGISTRY_HOST}"
fi

for svc in backend frontend admin; do
  echo "🚧 构建并推送 ${svc} ..."
  docker buildx build \
    --platform linux/amd64 \
    -t "${REGISTRY}/xavierblog-${svc}:${TAG}" \
    --push "${svc}"
done

echo "✅ 推送完成，服务器执行以下命令即可更新："
echo "   docker compose pull && docker compose up -d"
