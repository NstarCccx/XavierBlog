/** 分类、标签、评论、站点信息接口。 */
import { http } from './http'
import type { Category, Comment, SiteInfo, Tag } from '@/types'

export async function getCategories(): Promise<Category[]> {
  const { data } = await http.get('/categories')
  return data
}

export async function getTags(): Promise<Tag[]> {
  const { data } = await http.get('/tags')
  return data
}

export async function getPostComments(postId: number): Promise<Comment[]> {
  const { data } = await http.get(`/posts/${postId}/comments`)
  return data
}

export async function createComment(payload: {
  post_id: number
  parent_id?: number | null
  nickname: string
  email?: string
  content: string
}): Promise<{ id: number; message: string }> {
  const { data } = await http.post('/comments', payload)
  return data
}

export async function getSiteInfo(): Promise<SiteInfo> {
  const { data } = await http.get('/site-info')
  return data
}
