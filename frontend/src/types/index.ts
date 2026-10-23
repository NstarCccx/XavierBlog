/** 与后端 schemas 一一对应的类型定义（数据契约）。 */

export interface CategoryBrief {
  id: number
  name: string
  slug: string
}

export interface TagBrief {
  id: number
  name: string
  slug: string
}

export interface Category extends CategoryBrief {
  description: string
  post_count: number
  created_at: string
}

export interface Tag extends TagBrief {
  post_count: number
  created_at: string
}

export interface PostBrief {
  id: number
  title: string
  slug: string
  summary: string
  cover: string
  status: 'draft' | 'published'
  views: number
  is_pinned: boolean
  published_at: string | null
  category: CategoryBrief | null
  tags: TagBrief[]
}

export interface Post extends PostBrief {
  content: string
  created_at: string
  updated_at: string
}

export interface ArchiveItem {
  id: number
  title: string
  slug: string
  published_at: string | null
  category: CategoryBrief | null
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Comment {
  id: number
  nickname: string
  content: string
  is_author: boolean
  created_at: string
  replies: Comment[]
}

export interface User {
  id: number
  username: string
  nickname: string
  avatar: string
  /** admin 为博主，member 为前台注册用户 */
  role: 'admin' | 'member'
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SiteInfo {
  site_name: string
  site_description: string
  about_content: string
  footer: string
  /** ICP 备案号，如「粤ICP备2026162376号」。 */
  icp_number: string
  /** ICP 备案查询链接。 */
  icp_link: string
  /** 公安备案号，如「粤公网安备 XXXXXXXXXXXXXX号」，未下发时为空串。 */
  police_number: string
  /** 公安备案查询链接。 */
  police_link: string
}
