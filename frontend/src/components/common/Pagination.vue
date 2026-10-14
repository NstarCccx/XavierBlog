<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useLocale } from '@/composables/useLocale'

const props = defineProps<{
  page: number
  total: number
  pageSize: number
}>()

const emit = defineEmits<{ 'update:page': [page: number] }>()

const { t } = useLocale()

const pageCount = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

/* 窄屏只显示 3 个页码，避免分页器溢出视口 */
const isNarrow = ref(false)
const mq: MediaQueryList | null =
  typeof window !== 'undefined' ? window.matchMedia('(max-width: 480px)') : null
function updateNarrow() {
  if (mq) isNarrow.value = mq.matches
}
onMounted(() => {
  updateNarrow()
  mq?.addEventListener('change', updateNarrow)
})
onBeforeUnmount(() => mq?.removeEventListener('change', updateNarrow))

const pages = computed(() => {
  // 桌面最多 7 个页码、窄屏 3 个，当前页居中
  const count = Math.min(isNarrow.value ? 3 : 7, pageCount.value)
  let start = Math.max(1, props.page - Math.floor(count / 2))
  start = Math.min(start, pageCount.value - count + 1)
  return Array.from({ length: count }, (_, i) => start + i)
})

function go(p: number) {
  if (p >= 1 && p <= pageCount.value && p !== props.page) emit('update:page', p)
}
</script>

<template>
  <nav v-if="pageCount > 1" class="flex flex-wrap items-center justify-center gap-1 pt-4">
    <button
      class="rounded-lg px-2 py-1.5 text-xs text-stone-500 transition-colors hover:bg-stone-200/70 hover:text-stone-800 disabled:opacity-40 sm:px-3 sm:text-sm dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
      :disabled="page <= 1"
      @click="go(page - 1)"
    >
      {{ t('page.prev') }}
    </button>
    <button
      v-for="p in pages"
      :key="p"
      class="min-w-8 rounded-lg px-2 py-1.5 text-xs transition-colors sm:text-sm"
      :class="
        p === page
          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30'
          : 'text-stone-600 hover:bg-stone-200/70 dark:text-stone-300 dark:hover:bg-stone-800'
      "
      @click="go(p)"
    >
      {{ p }}
    </button>
    <button
      class="rounded-lg px-2 py-1.5 text-xs text-stone-500 transition-colors hover:bg-stone-200/70 hover:text-stone-800 disabled:opacity-40 sm:px-3 sm:text-sm dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
      :disabled="page >= pageCount"
      @click="go(page + 1)"
    >
      {{ t('page.next') }}
    </button>
  </nav>
</template>
