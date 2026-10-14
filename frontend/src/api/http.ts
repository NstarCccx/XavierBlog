/** axios 实例：统一 baseURL、错误提示。 */
import axios from 'axios'

/** 后端服务地址：换环境（部署/内网 IP）只改这里；vite 开发代理引用同一常量。 */
export const API_BASE = 'http://127.0.0.1:8000'

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
