import axios from 'axios'

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
