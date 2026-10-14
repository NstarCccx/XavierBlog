<script setup lang="ts">
/** 统一的页面头部：标题 + 描述 + 右侧操作区，所有管理页共用。 */
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-gray-900">{{ title }}</h1>
      <p v-if="description" class="mt-1 text-sm text-gray-400">{{ description }}</p>
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <slot />
    </div>
  </div>
</template>
