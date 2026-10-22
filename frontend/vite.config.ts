import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'


export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
  server: {
    port: 8082,
    host: '0.0.0.0',
    proxy: {
      // API 请求代理到 FastAPI，免跨域（与 admin 一致，浏览器始终请求同源 /api）
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      // 后台图片以 /uploads/... 相对地址引用时同样代理到后端静态目录
      '^/uploads/.+\\.(?:jpg|jpeg|png|gif|webp|svg)$': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  }
})
