<script setup lang="ts">
import { useSiteStore } from '@/stores/site'
import { useLocale } from '@/composables/useLocale'

const site = useSiteStore()
const { t } = useLocale()
</script>

<template>
  <div class="flex flex-col items-center px-4 py-24 text-center">
    <p class="mb-3 bg-gradient-to-br from-indigo-500 via-violet-500 to-cyan-400 bg-clip-text font-mono text-7xl font-bold text-transparent">
      404
    </p>
    <p class="mb-8 text-stone-500 dark:text-stone-400">{{ t('nf.desc') }}</p>
    <router-link :to="{ name: 'home' }" class="btn-primary">
      {{ t('nf.back') }} · {{ site.info.site_name }}
    </router-link>
  </div>
</template>
