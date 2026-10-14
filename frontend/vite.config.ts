import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

/** 后端 FastAPI 地址：单一来源在 src/api/http.ts 的 API_BASE，此处仅引用 */
import { API_BASE } from './src/api/http.ts'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 8082,
    host: '0.0.0.0',
    proxy: {
      // 开发环境代理到 FastAPI，免跨域
      '/api': { target: API_BASE, changeOrigin: true },
      '/uploads': { target: API_BASE, changeOrigin: true },
    },
  },
})
