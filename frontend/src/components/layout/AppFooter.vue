<script setup lang="ts">
import { useSiteStore } from '@/stores/site'

const site = useSiteStore()
</script>

<template>
  <footer
    class="border-t border-stone-200/70 bg-white/60 py-6 text-center text-sm text-stone-400 backdrop-blur dark:border-stone-800/70 dark:bg-[#0a0c12]/60"
  >
    <p class="font-mono text-xs">
      {{ site.info.footer || `© ${new Date().getFullYear()} ${site.info.site_name}` }}
    </p>
  </footer>
</template>
