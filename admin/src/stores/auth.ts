/** 认证状态：token、当前管理员。 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMe, login as apiLogin } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('admin_token') ?? '')
  const nickname = ref('')
  const username = ref('')

  async function login(user: string, password: string) {
    const jwt = await apiLogin(user, password)
    token.value = jwt
    localStorage.setItem('admin_token', jwt)
    await loadMe()
  }

  async function loadMe() {
    if (!token.value) return
    try {
      const me = await getMe()
      nickname.value = me.nickname || me.username
      username.value = me.username
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    nickname.value = ''
    username.value = ''
    localStorage.removeItem('admin_token')
  }

  return { token, nickname, username, login, loadMe, logout }
})
