/** 文章分页列表的复用逻辑：加载、分页、加载态。 */
import { ref, watch } from 'vue'
import { getPosts, type PostQuery } from '@/api/posts'
import type { PostBrief } from '@/types'

export function usePostList(buildQuery: () => PostQuery) {
  const posts = ref<PostBrief[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = 10
  const loading = ref(false)
  const error = ref('')

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const result = await getPosts({ ...buildQuery(), page: page.value, page_size: pageSize })
      posts.value = result.items
      total.value = result.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
      loading.value = false
    }
  }

  watch(page, load)

  return { posts, total, page, pageSize, loading, error, load }
}
