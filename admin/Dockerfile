# 管理后台镜像：多阶段构建，node 编译 → nginx 托管静态文件。
# vite build 时 base='/admin/'（见 vite.config.ts），产物拷到 html/admin/ 下，
# 容器内即以 /admin/ 子路径提供访问；API 走同源由外层网关反代。
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html/admin
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
