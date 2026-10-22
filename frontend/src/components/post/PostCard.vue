<script setup lang="ts">
import type { PostBrief } from '@/types'
import { formatDate } from '@/utils/format'
import { useLocale } from '@/composables/useLocale'

defineProps<{ post: PostBrief }>()

const { t } = useLocale()
</script>

<template>
  <article
    class="group relative overflow-hidden rounded-xl border border-stone-200/80 bg-white/70 p-5 shadow-sm backdrop-blur-xl transition-all duration-300 hover:-translate-y-0.5 hover:border-indigo-300/70 hover:shadow-lg hover:shadow-indigo-500/10 dark:border-stone-800 dark:bg-stone-900/60 dark:hover:border-indigo-500/40 dark:hover:shadow-indigo-500/10"
  >
    <!-- 悬停时的顶部流光线 -->
    <span
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      aria-hidden="true"
    />

    <div v-if="post.cover" class="mb-3 -mx-5 -mt-5 overflow-hidden rounded-t-xl">
      <img :src="post.cover" :alt="post.title" class="h-40 w-full object-cover" />
    </div>

    <div class="mb-2 flex flex-wrap items-center gap-3 font-mono text-xs text-stone-400 dark:text-stone-500">
      <span
        v-if="post.is_pinned"
        class="rounded-md bg-amber-100/80 px-2 py-0.5 font-semibold text-amber-600 dark:bg-amber-500/15 dark:text-amber-400"
      >
        {{ t('post.pinned') }}
      </span>
      <span>{{ formatDate(post.published_at) }}</span>
      <router-link
        v-if="post.category"
        :to="{ name: 'category', params: { slug: post.category.slug } }"
        class="text-indigo-500 hover:underline dark:text-indigo-400"
      >
        {{ post.category.name }}
      </router-link>
      <span>{{ t('post.views', { n: post.views }) }}</span>
    </div>

    <h2 class="mb-2 text-lg font-bold">
      <router-link
        :to="{ name: 'post-detail', params: { slug: post.slug } }"
        class="bg-gradient-to-r from-indigo-600 to-violet-600 bg-[length:0%_2px] bg-left-bottom bg-no-repeat pb-0.5 text-stone-900 transition-[background-size,color] duration-300 hover:bg-[length:100%_2px] dark:from-indigo-400 dark:to-violet-400 dark:text-stone-100"
      >
        {{ post.title }}
      </router-link>
    </h2>

    <p class="mb-3 line-clamp-2 text-sm text-stone-500 dark:text-stone-400">{{ post.summary }}</p>

    <div v-if="post.tags.length" class="flex flex-wrap gap-2">
      <router-link
        v-for="tag in post.tags"
        :key="tag.id"
        :to="{ name: 'tag', params: { slug: tag.slug } }"
        class="rounded-md bg-stone-100/80 px-2 py-0.5 font-mono text-xs text-stone-500 transition-colors hover:bg-indigo-50 hover:text-indigo-600 dark:bg-stone-800/70 dark:text-stone-400 dark:hover:bg-indigo-500/15 dark:hover:text-indigo-300"
      >
        # {{ tag.name }}
      </router-link>
    </div>
  </article>
</template>
