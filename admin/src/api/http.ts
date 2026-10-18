/** axios 实例：自动携带 token、401 统一跳登录、错误统一 ElMessage。 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

/** 后端服务地址：换环境（部署/内网 IP）只改这里；vite 开发代理引用同一常量。 */
// export const API_BASE = 'http://127.0.0.1:8000'
export const API_BASE = 'http://1.14.167.178:8000'

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 401) {
      localStorage.removeItem('admin_token')
      // BASE_URL：dev '/'，生产 '/admin/'，登录页始终在基路径下
      const loginPath = `${import.meta.env.BASE_URL}login`
      if (!location.pathname.startsWith(loginPath)) {
        ElMessage.error('登录已过期，请重新登录')
        location.href = loginPath
      }
    }
    return Promise.reject(new Error(typeof detail === 'string' ? detail : '请求失败'))
  },
)

export function errorMessage(e: unknown): string {
  return e instanceof Error ? e.message : '操作失败'
}
