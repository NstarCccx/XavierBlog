<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPostBySlug } from '@/api/posts'
import { renderMarkdown } from '@/utils/markdown'
import { formatDate } from '@/utils/format'
import { useLocale } from '@/composables/useLocale'
import CommentSection from '@/components/comment/CommentSection.vue'
import type { Post } from '@/types'

const route = useRoute()
const { t } = useLocale()
const post = ref<Post | null>(null)
const error = ref('')

const rendered = computed(() => (post.value ? renderMarkdown(post.value.content) : null))
const html = computed(() => rendered.value?.html ?? '')
const toc = computed(() => rendered.value?.toc ?? [])

/** 阅读时长：中文按 400 字/分钟、英文按 200 词/分钟估算 */
const readMinutes = computed(() => {
  if (!post.value) return 0
  const text = post.value.content
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[#>*`~|-]/g, ' ')
  const cjk = (text.match(/[\u4e00-\u9fff]/g) ?? []).length
  const words = (text.replace(/[\u4e00-\u9fff]/g, ' ').match(/[a-zA-Z0-9]+/g) ?? []).length
  return Math.max(1, Math.round(cjk / 400 + words / 200))
})

/* 目录滚动高亮（scrollspy） */
const activeId = ref('')

function updateActiveToc() {
  let current = toc.value[0]?.id ?? ''
  for (const item of toc.value) {
    const el = document.getElementById(item.id)
    if (el && el.getBoundingClientRect().top <= 100) current = item.id
  }
  activeId.value = current
}

function onScroll() {
  updateActiveToc()
}

async function load() {
  error.value = ''
  post.value = null
  try {
    post.value = await getPostBySlug(route.params.slug as string)
    document.title = `${post.value.title} - ${post.value.category?.name ?? ''}`
    await nextTick()
    updateActiveToc()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '文章加载失败'
  }
}

onMounted(() => {
  load()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
watch(() => route.params.slug, load)
</script>

<template>
  <div class="px-4 py-10">
    <p v-if="error" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ error }}</p>
    <p v-else-if="!post" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ t('common.loading') }}</p>

    <article v-else>
      <!-- 文章头部：元信息 → 大标题 → 标签 → 渐变分隔线 → 封面 -->
      <header class="mb-10">
        <div class="mb-4 flex flex-wrap items-center gap-x-4 gap-y-2 font-mono text-xs text-stone-400 dark:text-stone-500">
          <span class="inline-flex items-center gap-1.5">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /></svg>
            {{ formatDate(post.published_at) }}
          </span>
          <span class="inline-flex items-center gap-1.5">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
            {{ t('detail.readTime', { n: readMinutes }) }}
          </span>
          <span class="inline-flex items-center gap-1.5">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
            {{ t('post.views', { n: post.views }) }}
          </span>
          <router-link
            v-if="post.category"
            :to="{ name: 'category', params: { slug: post.category.slug } }"
            class="inline-flex items-center gap-1.5 transition-colors hover:text-indigo-500 dark:hover:text-indigo-400"
          >
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /></svg>
            {{ post.category.name }}
          </router-link>
        </div>

        <h1 class="text-3xl leading-tight font-bold text-stone-900 sm:text-4xl dark:text-stone-100">
          {{ post.title }}
        </h1>

        <div v-if="post.tags.length" class="mt-5 flex flex-wrap gap-2">
          <router-link
            v-for="tag in post.tags"
            :key="tag.id"
            :to="{ name: 'tag', params: { slug: tag.slug } }"
            class="rounded-full border border-stone-200 bg-white/50 px-3 py-0.5 text-xs text-stone-500 transition-all hover:border-indigo-300 hover:text-indigo-600 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-400 dark:hover:border-indigo-500/50 dark:hover:text-indigo-400"
          >
            # {{ tag.name }}
          </router-link>
        </div>

        <div
          class="mt-8 h-px bg-gradient-to-r from-indigo-400/50 via-stone-200 to-transparent dark:from-indigo-500/40 dark:via-stone-700"
          aria-hidden="true"
        />

        <div v-if="post.cover" class="mt-8 overflow-hidden rounded-2xl shadow-lg ring-1 ring-stone-900/5 dark:ring-white/10">
          <img :src="post.cover" :alt="post.title" class="w-full object-cover" style="max-height: 420px" />
        </div>
      </header>

      <div class="flex gap-8">
        <div class="markdown-body min-w-0 flex-1" v-html="html" />

        <!-- 目录：随滚动高亮当前小节 -->
        <aside v-if="toc.length" class="sticky top-20 hidden h-fit w-52 shrink-0 lg:block">
          <p class="mb-3 text-sm font-semibold text-stone-900 dark:text-stone-100">{{ t('detail.toc') }}</p>
          <ul class="space-y-0.5 text-sm">
            <li v-for="item in toc" :key="item.id">
              <a
                :href="`#${item.id}`"
                class="-ml-4 block truncate border-l-2 py-1 pl-3 transition-all"
                :class="[
                  item.level === 3 && 'pl-5',
                  activeId === item.id
                    ? 'border-indigo-500 font-medium text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-stone-400 hover:text-indigo-600 dark:text-stone-500 dark:hover:text-indigo-400',
                ]"
              >
                {{ item.text }}
              </a>
            </li>
          </ul>
        </aside>
      </div>

      <!-- 全文完分隔 -->
      <div class="mt-14 flex items-center gap-3" aria-hidden="true">
        <span class="h-px flex-1 bg-gradient-to-r from-transparent to-stone-300 dark:to-stone-700" />
        <span class="font-mono text-[11px] tracking-[0.4em] text-stone-400 uppercase dark:text-stone-500">
          {{ t('detail.end') }}
        </span>
        <span class="h-px flex-1 bg-gradient-to-l from-transparent to-stone-300 dark:to-stone-700" />
      </div>

      <CommentSection :post-id="post.id" class="mt-12" />
    </article>
  </div>
</template>
