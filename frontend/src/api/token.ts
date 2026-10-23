/** 登录 token 的存取（localStorage），前后端交互的唯一凭证来源。 */
const TOKEN_KEY = 'xb-token'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(value: string): void {
  if (value) {
    localStorage.setItem(TOKEN_KEY, value)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}
