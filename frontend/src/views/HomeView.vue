<script setup lang="ts">
import { onMounted } from 'vue'
import { usePostList } from '@/composables/usePostList'
import PostCard from '@/components/post/PostCard.vue'
import Pagination from '@/components/common/Pagination.vue'
import HeroGlass from '@/components/home/HeroGlass.vue'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()
const { posts, total, page, pageSize, loading, error, load } = usePostList(() => ({}))

onMounted(load)
</script>

<template>
  <HeroGlass />

  <section id="posts" class="scroll-mt-20 px-4 pt-12 pb-16">
    <h2 class="mb-6 flex items-center gap-3 font-mono text-sm font-semibold tracking-widest text-stone-500 uppercase dark:text-stone-400">
      <span class="h-px flex-1 bg-gradient-to-r from-transparent via-indigo-400/50 to-indigo-400/50 dark:via-indigo-500/40 dark:to-indigo-500/40" />
      {{ t('home.latest') }}
      <span class="h-px w-10 bg-indigo-400/50 dark:bg-indigo-500/40" />
    </h2>

    <p v-if="error" class="rounded-lg border border-red-200 bg-red-50 p-4 text-center text-sm text-red-600 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-400">
      {{ error }}
    </p>
    <p v-else-if="loading" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ t('common.loading') }}</p>
    <p v-else-if="!posts.length" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ t('home.noPosts') }}</p>

    <div v-else class="space-y-4">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
      <Pagination v-model:page="page" :total="total" :page-size="pageSize" />
    </div>
  </section>
</template>
