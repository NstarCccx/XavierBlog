<script setup lang="ts">
import { computed } from 'vue'
import { useSiteStore } from '@/stores/site'

const site = useSiteStore()

/**
 * 备案信息：ICP 备案号 + 公安备案号。
 * 公安备案号未下发时为空串，此时该项不渲染，页脚只保留 ICP 备案。
 */
const filings = computed(() => {
  const { icp_number, icp_link, police_number, police_link } = site.info
  const items: { key: string; number: string; link: string }[] = []
  if (icp_number) {
    items.push({
      key: 'icp',
      number: icp_number,
      link: icp_link || 'https://beian.miit.gov.cn/',
    })
  }
  if (police_number) {
    items.push({
      key: 'police',
      number: police_number,
      link: police_link || 'https://beian.mps.gov.cn/',
    })
  }
  return items
})
</script>

<template>
  <footer
    class="border-t border-stone-200/70 bg-white/60 py-6 text-center text-sm text-stone-400 backdrop-blur dark:border-stone-800/70 dark:bg-[#0a0c12]/60"
  >
    <p class="font-mono text-xs">
      {{ site.info.footer || `© ${new Date().getFullYear()} ${site.info.site_name}` }}
    </p>

    <!-- 备案信息：ICP 备案 + 公安备案（公安备案号下发后自动出现） -->
    <div
      v-if="filings.length"
      class="mt-2 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs"
    >
      <component
        :is="item.link ? 'a' : 'span'"
        v-for="item in filings"
        :key="item.key"
        :href="item.link || undefined"
        :target="item.link ? '_blank' : undefined"
        :rel="item.link ? 'noopener noreferrer' : undefined"
        class="inline-flex items-center gap-1 transition-colors"
        :class="item.link ? 'hover:text-stone-600 dark:hover:text-stone-200' : ''"
      >
        <!-- 公安备案图标：按监管要求置于备案号链接内、号码左侧 -->
        <img
          v-if="item.key === 'police'"
          src="https://beian.mps.gov.cn/img/logo.png"
          alt="公安备案图标"
          class="h-4 w-4"
        />
        {{ item.number }}
      </component>
    </div>
  </footer>
</template>
