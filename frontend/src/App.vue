<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AuthModal from '@/components/auth/AuthModal.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(() => {
  auth.ensureMe()
})
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <AppHeader />
    <main class="mx-auto w-full max-w-4xl flex-1">
      <router-view />
    </main>
    <AppFooter />
    <AuthModal />
  </div>
</template>
