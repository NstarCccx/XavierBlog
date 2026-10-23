/** 前台用户登录态：token 持久化到 localStorage，启动时拉取一次 me。 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'
import { getToken, setToken as persistToken } from '@/api/token'
import { UNAUTHORIZED_EVENT } from '@/api/http'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getToken())
  const user = ref<User | null>(null)
  /** 启动时的 me 请求是否已结束（避免顶栏闪烁登录按钮） */
  const ready = ref(false)
  /** 登录/注册弹窗开关，顶栏与评论区共用 */
  const modalOpen = ref(false)

  function applyAuth(accessToken: string, u: User) {
    token.value = accessToken
    persistToken(accessToken)
    user.value = u
  }

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    applyAuth(res.access_token, res.user)
  }

  async function register(payload: { username: string; nickname: string; password: string }) {
    const res = await authApi.register(payload)
    applyAuth(res.access_token, res.user)
  }

  function logout() {
    token.value = ''
    persistToken('')
    user.value = null
  }

  /** 应用启动时恢复登录态；token 失效则由 401 拦截器打回未登录 */
  async function ensureMe() {
    if (!token.value) {
      ready.value = true
      return
    }
    try {
      user.value = await authApi.fetchMe()
    } catch {
      logout()
    } finally {
      ready.value = true
    }
  }

  function openModal() {
    modalOpen.value = true
  }
  function closeModal() {
    modalOpen.value = false
  }

  // token 被任意接口判失效（401）时，统一回到未登录态
  window.addEventListener(UNAUTHORIZED_EVENT, logout)

  return { token, user, ready, modalOpen, login, register, logout, ensureMe, openModal, closeModal }
})
