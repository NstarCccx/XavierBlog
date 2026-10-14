/** 文章相关接口。 */
import { http } from './http'
import type { ArchiveItem, PageResult, Post, PostBrief } from '@/types'

export interface PostQuery {
  page?: number
  page_size?: number
  category?: string
  tag?: string
  keyword?: string
}

export async function getPosts(query: PostQuery = {}): Promise<PageResult<PostBrief>> {
  const { data } = await http.get('/posts', { params: query })
  return data
}

export async function getPostBySlug(slug: string): Promise<Post> {
  const { data } = await http.get(`/posts/${slug}`)
  return data
}

export async function getArchive(): Promise<ArchiveItem[]> {
  const { data } = await http.get('/posts/archive')
  return data
}
