import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

/** 后端 FastAPI 地址（与 src/api/http.ts 的 API_BASE 保持一致） */
const BACKEND = 'http://127.0.0.1:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],

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
      // 后台上传的图片以相对地址 /uploads/... 引用，需代理到后端静态目录；
      // 只匹配图片文件：裸 /uploads 留给管理端「图片库」页面的 SPA 路由，
      // 否则刷新该页会被代理到后端而 404
      '^/uploads/.+\\.(?:jpg|jpeg|png|gif|webp|svg)$': {
        target: BACKEND,
        changeOrigin: true,
      },
    },
  },
})
