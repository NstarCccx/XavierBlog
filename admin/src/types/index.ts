/** 与后端 schemas 一一对应的类型定义。 */

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

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
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

export interface Category extends CategoryBrief {
  description: string
  post_count: number
  created_at: string
}

export interface Tag extends TagBrief {
  post_count: number
  created_at: string
}

export interface CommentAdmin {
  id: number
  post_id: number
  post_title: string
  parent_id: number | null
  nickname: string
  email: string
  content: string
  status: 'pending' | 'approved'
  is_author: boolean
  created_at: string
}

export interface PostViewsItem {
  id: number
  title: string
  views: number
}

export interface DashboardStats {
  post_count: number
  published_count: number
  draft_count: number
  category_count: number
  tag_count: number
  comment_count: number
  pending_comment_count: number
  total_views: number
  top_views: PostViewsItem[]
}

export interface AdminInfo {
  id: number
  username: string
  nickname: string
  avatar: string
}

export interface UploadItem {
  filename: string
  url: string
  size: number
  modified_at: string
}

/** 文章编辑表单数据 */
export interface PostForm {
  title: string
  slug: string
  summary: string
  content: string
  cover: string
  status: 'draft' | 'published'
  is_pinned: boolean
  category_id: number | null
  tag_ids: number[]
}
