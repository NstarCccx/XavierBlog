import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { API_BASE } from './src/api/http.ts'
export default defineConfig(({ command }) => ({
  plugins: [vue(), tailwindcss()],

  // 生产以 /admin/ 子路径部署（nginx 网关统一入口），本地 dev 仍在根路径
  base: command === 'build' ? '/admin/' : '/',

  resolve: {
    // 「@」指向 src 目录，import 里用 @/components/xxx
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 8083,
    host: '0.0.0.0',
    proxy: {
      // API 请求代理到 FastAPI，免跨域（与前台一致，浏览器始终请求同源 /api）
      '/api': { target: API_BASE, changeOrigin: true },
      // 后台上传的图片以相对地址 /uploads/... 引用，需代理到后端静态目录；
      // 只匹配图片文件：裸 /uploads 留给管理端「图片库」页面的 SPA 路由，
      // 否则刷新该页会被代理到后端而 404
      '^/uploads/.+\\.(?:jpg|jpeg|png|gif|webp|svg)$': {
        target: API_BASE,
        changeOrigin: true,
      },
    },
  },
}))
