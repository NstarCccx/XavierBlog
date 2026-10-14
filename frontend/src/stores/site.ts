/** 站点信息：启动时拉取一次，全局共享。 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSiteInfo } from '@/api/blog'
import type { SiteInfo } from '@/types'

export const useSiteStore = defineStore('site', () => {
  const info = ref<SiteInfo>({
    site_name: 'XavierBlog',
    site_description: '',
    about_content: '',
    footer: '',
  })

  async function load() {
    try {
      info.value = await getSiteInfo()
      document.title = info.value.site_name
    } catch {
      // 后端未启动时保持默认值
    }
  }

  return { info, load }
})
