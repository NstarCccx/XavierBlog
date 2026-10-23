/** 管理端全部接口（除上传外按模块拆分在此）。 */
import { http } from './http'
import type {
  AdminInfo,
  Category,
  CommentAdmin,
  DashboardStats,
  PageResult,
  Post,
  PostBrief,
  Tag,
  UserAdmin,
} from '@/types'

// ---------- 认证 ----------
export async function login(username: string, password: string): Promise<string> {
  const { data } = await http.post('/admin/auth/login', { username, password })
  return data.access_token as string
}

export async function getMe(): Promise<AdminInfo> {
  const { data } = await http.get('/admin/auth/me')
  return data
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  await http.put('/admin/auth/password', {
    old_password: oldPassword,
    new_password: newPassword,
  })
}

// ---------- 文章 ----------
export async function getPosts(params: {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}): Promise<PageResult<PostBrief>> {
  const { data } = await http.get('/admin/posts', { params })
  return data
}

export async function getPost(id: number): Promise<Post> {
  const { data } = await http.get(`/admin/posts/${id}`)
  return data
}

export async function createPost(payload: Record<string, unknown>): Promise<Post> {
  const { data } = await http.post('/admin/posts', payload)
  return data
}

export async function updatePost(id: number, payload: Record<string, unknown>): Promise<Post> {
  const { data } = await http.put(`/admin/posts/${id}`, payload)
  return data
}

export async function deletePost(id: number): Promise<void> {
  await http.delete(`/admin/posts/${id}`)
}

// ---------- 分类 ----------
export async function getCategories(): Promise<Category[]> {
  const { data } = await http.get('/admin/categories')
  return data
}

export async function createCategory(payload: { name: string; slug?: string; description?: string }): Promise<Category> {
  const { data } = await http.post('/admin/categories', payload)
  return data
}

export async function updateCategory(id: number, payload: Record<string, unknown>): Promise<Category> {
  const { data } = await http.put(`/admin/categories/${id}`, payload)
  return data
}

export async function deleteCategory(id: number): Promise<void> {
  await http.delete(`/admin/categories/${id}`)
}

// ---------- 标签 ----------
export async function getTags(): Promise<Tag[]> {
  const { data } = await http.get('/admin/tags')
  return data
}

export async function createTag(payload: { name: string; slug?: string }): Promise<Tag> {
  const { data } = await http.post('/admin/tags', payload)
  return data
}

export async function updateTag(id: number, payload: Record<string, unknown>): Promise<Tag> {
  const { data } = await http.put(`/admin/tags/${id}`, payload)
  return data
}

export async function deleteTag(id: number): Promise<void> {
  await http.delete(`/admin/tags/${id}`)
}

// ---------- 评论 ----------
export async function getComments(params: {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}): Promise<PageResult<CommentAdmin>> {
  const { data } = await http.get('/admin/comments', { params })
  return data
}

export async function approveComment(id: number): Promise<void> {
  await http.put(`/admin/comments/${id}/approve`)
}

export async function rejectComment(id: number): Promise<void> {
  await http.put(`/admin/comments/${id}/reject`)
}

export async function deleteComment(id: number): Promise<void> {
  await http.delete(`/admin/comments/${id}`)
}

export async function replyComment(id: number, content: string): Promise<void> {
  await http.post(`/admin/comments/${id}/reply`, { content })
}

// ---------- 用户 ----------
export async function getUsers(params: {
  page?: number
  page_size?: number
  keyword?: string
}): Promise<PageResult<UserAdmin>> {
  const { data } = await http.get('/admin/users', { params })
  return data
}

export async function resetUserPassword(id: number, newPassword: string): Promise<void> {
  await http.put(`/admin/users/${id}/password`, { new_password: newPassword })
}

// ---------- 仪表盘 / 设置 ----------
export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await http.get('/admin/dashboard/stats')
  return data
}

export async function getSiteConfig(): Promise<Record<string, string>> {
  const { data } = await http.get('/admin/site-config')
  return data
}

export async function updateSiteConfig(data: Record<string, string>): Promise<void> {
  await http.put('/admin/site-config', { data })
}

// ---------- 上传 ----------
export async function getUploads(): Promise<import('@/types').UploadItem[]> {
  const { data } = await http.get('/admin/uploads')
  return data
}

export async function deleteUpload(url: string): Promise<void> {
  await http.delete('/admin/uploads', { params: { url } })
}
