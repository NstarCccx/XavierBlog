#!/usr/bin/env bash
# 备案通过、域名解析生效后执行：签发 Let's Encrypt 证书并启用 HTTPS
# 用法：./enable-https.sh [邮箱]
set -euo pipefail
cd "$(dirname "$0")"

DOMAIN="guangxuan.xyz"
EMAIL="${1:-admin@${DOMAIN}}"

# ---------- 0. 前置检查 ----------
if ! grep -q "ssl_certificate" nginx/gateway.conf 2>/dev/null; then
  echo "🔍 检查域名解析..."
  SERVER_IP="$(curl -s -m 5 ifconfig.me || true)"
  check_dns() { getent hosts "$1" 2>/dev/null | awk '{print $1; exit}'; }
  APEX_IP="$(check_dns "$DOMAIN")"
  [[ -n "$APEX_IP" ]] || { echo "❌ $DOMAIN 还没有解析记录，先去 DNS 控制台添加 A 记录指向 $SERVER_IP"; exit 1; }
  [[ "$APEX_IP" == "$SERVER_IP" ]] || { echo "❌ $DOMAIN 当前解析到 $APEX_IP，不是本机 $SERVER_IP"; exit 1; }
  echo "✅ $DOMAIN -> $SERVER_IP"
  if WWW_IP="$(check_dns "www.$DOMAIN")" && [[ "$WWW_IP" == "$SERVER_IP" ]]; then
    HAS_WWW=1; echo "✅ www.$DOMAIN -> $WWW_IP"
  else
    HAS_WWW=0; echo "⚠️  www.$DOMAIN 未解析或指向不同 IP，本次只为 $DOMAIN 签发证书（建议补一条 www 的 A 记录）"
  fi
else
  echo "ℹ️  HTTPS 已启用，仅执行续期检查"
fi

# ---------- 1. 证书目录 ----------
mkdir -p certbot/www certbot/conf

# ---------- 2. 签发 / 续期 ----------
CERT_DIR="certbot/conf/live/$DOMAIN"
if [[ ! -f "$CERT_DIR/fullchain.pem" ]]; then
  echo "📜 向 Let's Encrypt 申请证书（邮箱 $EMAIL）..."
  D_ARGS=(-d "$DOMAIN")
  [[ "${HAS_WWW:-0}" == "1" ]] && D_ARGS+=(-d "www.$DOMAIN")
  docker compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    "${D_ARGS[@]}" \
    --email "$EMAIL" --agree-tos --no-eff-email --non-interactive
else
  echo "📜 证书已存在，跳过签发"
fi

# ---------- 3. 切换网关到 SSL 配置 ----------
cp nginx/gateway-ssl.conf nginx/gateway.conf.new
if [[ "${HAS_WWW:-0}" == "0" ]]; then
  sed -i.bak "s/ www\.${DOMAIN//./\\.}//g" nginx/gateway.conf.new && rm -f nginx/gateway.conf.new.bak
fi
cp nginx/gateway.conf nginx/gateway.conf.http-backup
mv nginx/gateway.conf.new nginx/gateway.conf

echo "🔁 应用新网关配置..."
if docker compose up -d nginx && docker compose exec nginx nginx -t; then
  docker compose exec nginx nginx -s reload
  echo "✅ HTTPS 已启用：https://$DOMAIN"
else
  echo "❌ SSL 配置校验失败，回退 HTTP 并重启"
  cp nginx/gateway.conf.http-backup nginx/gateway.conf
  docker compose up -d nginx
  exit 1
fi

# ---------- 4. 自动续期（每天 3:15 / 15:15 各检查一次） ----------
DEPLOY_DIR="$(pwd)"
CRON_LINE="15 3,15 * * * cd ${DEPLOY_DIR} && docker compose run --rm certbot renew --webroot -w /var/www/certbot --quiet && docker compose exec nginx nginx -s reload >/dev/null 2>&1"
if crontab -l 2>/dev/null | grep -qF "certbot renew"; then
  echo "✅ 续期定时任务已存在"
else
  ( crontab -l 2>/dev/null; echo "$CRON_LINE" ) | crontab -
  echo "✅ 已安装自动续期 crontab（crontab -l 可查看）"
fi
