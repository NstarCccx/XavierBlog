/** 前台用户认证接口。 */
import { http } from './http'
import type { AuthResponse, User } from '@/types'

export async function login(username: string, password: string): Promise<AuthResponse> {
  const { data } = await http.post('/auth/login', { username, password })
  return data
}

export async function register(payload: {
  username: string
  nickname: string
  password: string
}): Promise<AuthResponse> {
  const { data } = await http.post('/auth/register', payload)
  return data
}

export async function fetchMe(): Promise<User> {
  const { data } = await http.get('/auth/me')
  return data
}
