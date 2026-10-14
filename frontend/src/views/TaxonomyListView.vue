<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePostList } from '@/composables/usePostList'
import PostCard from '@/components/post/PostCard.vue'
import Pagination from '@/components/common/Pagination.vue'
import { useLocale } from '@/composables/useLocale'

const props = defineProps<{ type: 'category' | 'tag' }>()

const route = useRoute()
const { t } = useLocale()
const { posts, total, page, pageSize, loading, load } = usePostList(() => ({
  [props.type]: route.params.slug as string,
}))

const title = computed(() =>
  t(props.type === 'category' ? 'tax.title.category' : 'tax.title.tag', {
    slug: route.params.slug as string,
  }),
)

function loadFirst() {
  page.value = 1
  load()
}

onMounted(loadFirst)
watch(() => route.params.slug, loadFirst)
</script>

<template>
  <div class="px-4 py-10">
    <header class="mb-8">
      <h1 class="mb-1 text-2xl font-bold text-stone-900 dark:text-stone-100">{{ title }}</h1>
      <p class="font-mono text-sm text-stone-400 dark:text-stone-500">{{ t('tax.total', { n: total }) }}</p>
    </header>

    <p v-if="loading" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ t('common.loading') }}</p>
    <p v-else-if="!posts.length" class="py-16 text-center text-stone-400 dark:text-stone-500">
      {{ t(props.type === 'category' ? 'tax.empty.category' : 'tax.empty.tag') }}
    </p>

    <div v-else class="space-y-4">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
      <Pagination v-model:page="page" :total="total" :page-size="pageSize" />
    </div>
  </div>
</template>
