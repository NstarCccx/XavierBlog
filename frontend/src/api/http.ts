import axios from 'axios'
import { getToken, setToken } from './token'

// 生产环境由 Nginx 反向代理到 FastAPI
export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** token 失效时通知界面回到未登录态（auth store 监听） */
export const UNAUTHORIZED_EVENT = 'xb:unauthorized'

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response?.status === 401 && getToken()) {
      setToken('')
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    const message =
      error.response?.data?.detail || error.message || '请求失败，请稍后重试'
    return Promise.reject(new Error(typeof message === 'string' ? message : '请求失败'))
  },
)
