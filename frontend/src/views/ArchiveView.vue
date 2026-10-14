<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getArchive } from '@/api/posts'
import { formatDate } from '@/utils/format'
import { formatMonth, useLocale } from '@/composables/useLocale'
import type { ArchiveItem, CategoryBrief } from '@/types'

const { t } = useLocale()

const items = ref<ArchiveItem[]>([])
const loading = ref(true)
const selectedCategory = ref<string | null>(null)

const categories = computed(() => {
  const map = new Map<string, CategoryBrief>()
  for (const item of items.value) {
    if (item.category) {
      map.set(item.category.slug, item.category)
    }
  }
  return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name))
})

const filteredItems = computed(() => {
  if (!selectedCategory.value) return items.value
  return items.value.filter(item => item.category?.slug === selectedCategory.value)
})

const groupedByMonth = computed(() => {
  const map = new Map<string, ArchiveItem[]>()
  for (const item of filteredItems.value) {
    const date = item.published_at ? new Date(item.published_at) : new Date()
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    map.set(key, [...(map.get(key) ?? []), item])
  }
  return [...map.entries()]
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([key, list]) => {
      const [year, month] = key.split('-')
      const date = new Date(Number(year), Number(month) - 1)
      return {
        label: formatMonth(date.getFullYear(), date.getMonth() + 1),
        items: list,
      }
    })
})

function selectCategory(slug: string | null) {
  selectedCategory.value = slug
}

onMounted(async () => {
  try {
    items.value = await getArchive()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="px-4 py-10">
    <!-- 页头：渐变标题 + 总数 -->
    <header class="mb-10 text-center">
      <h1
        class="bg-gradient-to-r from-indigo-600 via-violet-600 to-cyan-500 bg-clip-text text-3xl font-bold tracking-tight text-transparent sm:text-4xl dark:from-indigo-400 dark:via-violet-400 dark:to-cyan-300"
      >
        {{ t('archive.title') }}
      </h1>
      <p class="mt-3 font-mono text-sm tracking-widest text-stone-400 dark:text-stone-500">
        {{ t('archive.total', { n: items.length }) }}
      </p>
      <div class="mx-auto mt-7 flex max-w-xs items-center gap-3" aria-hidden="true">
        <span class="h-px flex-1 bg-gradient-to-r from-transparent to-indigo-400/60 dark:to-indigo-500/40" />
        <span class="font-mono text-[11px] tracking-[0.35em] text-indigo-500/80 uppercase dark:text-cyan-300/80">ARCHIVE</span>
        <span class="h-px flex-1 bg-gradient-to-l from-transparent to-indigo-400/60 dark:to-indigo-500/40" />
      </div>
    </header>

    <p v-if="loading" class="py-16 text-center text-stone-400 dark:text-stone-500">{{ t('common.loading') }}</p>

    <template v-else>
      <!-- 分类筛选 -->
      <div class="mb-10 flex flex-wrap justify-center gap-2.5">
        <button
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm transition-all"
          :class="
            selectedCategory === null
              ? 'border-transparent bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/30'
              : 'border-stone-200 bg-white/70 text-stone-600 hover:border-indigo-400 hover:text-indigo-600 dark:border-stone-700/80 dark:bg-stone-800/60 dark:text-stone-400 dark:hover:border-indigo-500 dark:hover:text-indigo-400'
          "
          @click="selectCategory(null)"
        >
          {{ t('archive.all') }}
          <span class="ml-1.5 text-xs opacity-70">({{ items.length }})</span>
        </button>
        <button
          v-for="cat in categories"
          :key="cat.slug"
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm transition-all"
          :class="
            selectedCategory === cat.slug
              ? 'border-transparent bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/30'
              : 'border-stone-200 bg-white/70 text-stone-600 hover:border-indigo-400 hover:text-indigo-600 dark:border-stone-700/80 dark:bg-stone-800/60 dark:text-stone-400 dark:hover:border-indigo-500 dark:hover:text-indigo-400'
          "
          @click="selectCategory(cat.slug)"
        >
          {{ cat.name }}
          <span class="ml-1.5 text-xs opacity-70">({{ items.filter(i => i.category?.slug === cat.slug).length }})</span>
        </button>
      </div>

      <!-- 空状态 -->
      <div
        v-if="!filteredItems.length"
        class="rounded-2xl border border-dashed border-stone-300 py-16 text-center text-stone-400 dark:border-stone-700 dark:text-stone-500"
      >
        {{ t('archive.empty') }}
      </div>

      <!-- 按月分组的时间线 -->
      <section v-else class="space-y-12">
        <div v-for="group in groupedByMonth" :key="group.label">
          <h2 class="mb-5 flex items-center gap-3 font-mono text-sm font-semibold tracking-widest text-stone-500 uppercase dark:text-stone-400">
            <span class="h-px w-10 bg-indigo-400/50 dark:bg-indigo-500/40" aria-hidden="true" />
            {{ group.label }}
            <span class="rounded-full bg-stone-100 px-2 py-0.5 text-[11px] font-normal tracking-normal text-stone-500 dark:bg-stone-800 dark:text-stone-400">
              {{ t('archive.count', { n: group.items.length }) }}
            </span>
            <span class="h-px flex-1 bg-gradient-to-r from-indigo-400/40 to-transparent dark:from-indigo-500/30" aria-hidden="true" />
          </h2>

          <ul class="relative space-y-1 border-l-2 border-stone-200 pl-6 dark:border-stone-800">
            <li v-for="item in group.items" :key="item.id" class="relative">
              <span
                class="absolute top-1/2 -left-[31px] h-2.5 w-2.5 -translate-y-1/2 rounded-full bg-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.6)] transition-transform group-hover:scale-125 dark:bg-indigo-500"
                aria-hidden="true"
              />
              <router-link
                :to="{ name: 'post-detail', params: { slug: item.slug } }"
                class="group -mx-3 flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-stone-100/80 dark:hover:bg-stone-800/40"
              >
                <span
                  class="truncate text-stone-700 transition-colors group-hover:text-indigo-600 dark:text-stone-300 dark:group-hover:text-indigo-400"
                >
                  {{ item.title }}
                </span>
                <span
                  v-if="item.category"
                  class="shrink-0 rounded-full bg-stone-100 px-2 py-0.5 text-xs text-stone-500 transition-colors group-hover:bg-indigo-50 group-hover:text-indigo-600 dark:bg-stone-800 dark:text-stone-400 dark:group-hover:bg-indigo-500/10 dark:group-hover:text-indigo-400"
                >
                  {{ item.category.name }}
                </span>
                <span class="ml-auto shrink-0 font-mono text-xs text-stone-400 dark:text-stone-500">
                  {{ formatDate(item.published_at) }}
                </span>
              </router-link>
            </li>
          </ul>
        </div>
      </section>
    </template>
  </div>
</template>
