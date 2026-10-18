import axios from 'axios'

// 开发环境
// export const API_BASE = 'http://127.0.0.1:8000'
export const API_BASE = 'http://1.14.167.178:8000'

// 生产环境由 Nginx 反向代理到 FastAPI
export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || '请求失败，请稍后重试'
    return Promise.reject(new Error(typeof message === 'string' ? message : '请求失败'))
  },
)
