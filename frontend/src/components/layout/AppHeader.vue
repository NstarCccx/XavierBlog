<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSiteStore } from '@/stores/site'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { useLocale } from '@/composables/useLocale'

const site = useSiteStore()
const auth = useAuthStore()
const route = useRoute()
const { theme, toggle: toggleTheme } = useTheme()
const { t, locale, setLocale } = useLocale()

const links = computed(() => [
  { name: 'home', label: t('nav.home') },
  { name: 'archive', label: t('nav.archive') },
  { name: 'about', label: t('nav.about') },
])

/* 移动端汉堡菜单：切页自动收起 */
const menuOpen = ref(false)
/* 桌面端用户菜单 */
const userMenuOpen = ref(false)
watch(() => route.fullPath, () => { menuOpen.value = false; userMenuOpen.value = false })

const userInitial = computed(
  () => (auth.user?.nickname || auth.user?.username || '?').trim().charAt(0).toUpperCase(),
)

function logout() {
  userMenuOpen.value = false
  menuOpen.value = false
  auth.logout()
}

onMounted(site.load)
</script>

<template>
  <header
    class="sticky top-0 z-30 border-b border-stone-200/70 bg-white/70 backdrop-blur-xl dark:border-stone-800/70 dark:bg-[#0a0c12]/70"
  >
    <div class="mx-auto flex h-16 max-w-4xl items-center justify-between gap-2 px-4 sm:gap-3">
      <router-link :to="{ name: 'home' }" class="flex shrink-0 items-center gap-2">
        <span
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 font-mono text-sm font-bold text-white shadow-lg shadow-indigo-500/30"
        >
          X
        </span>
        <span
          class="font-mono text-lg font-bold tracking-tight text-stone-900 max-sm:hidden dark:text-stone-100"
        >
          {{ site.info.site_name }}
        </span>
      </router-link>

      <div class="flex items-center gap-2 sm:gap-5">
        <nav class="hidden items-center gap-3 sm:flex sm:gap-6">
          <router-link
            v-for="link in links"
            :key="link.name"
            :to="{ name: link.name }"
            class="group relative flex h-16 items-center text-[13px] transition-colors sm:text-sm"
            :class="
              route.name === link.name
                ? 'font-medium text-indigo-600 dark:text-indigo-400'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100'
            "
          >
            {{ link.label }}
            <span
              class="absolute bottom-0 left-0 h-0.5 w-full origin-left rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-transform duration-300"
              :class="route.name === link.name ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'"
            />
          </router-link>
        </nav>

        <!-- 登录入口 / 用户菜单 -->
        <div v-if="!auth.ready" class="h-8 w-20" aria-hidden="true" />
        <button
          v-else-if="!auth.user"
          type="button"
          class="shrink-0 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-md shadow-indigo-500/30 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/40 active:translate-y-0 sm:px-4"
          @click="auth.openModal()"
        >
          {{ t('comment.loginBtn') }}
        </button>
        <div v-else class="relative shrink-0">
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-full border border-stone-200 bg-white/80 py-1 pr-2.5 pl-1 text-xs text-stone-600 shadow-sm backdrop-blur transition-colors hover:border-indigo-300 dark:border-stone-700 dark:bg-stone-800/80 dark:text-stone-300 dark:hover:border-indigo-500/50"
            :aria-expanded="userMenuOpen"
            @click="userMenuOpen = !userMenuOpen"
          >
            <span
              class="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 text-[11px] font-bold text-white"
              aria-hidden="true"
            >
              {{ userInitial }}
            </span>
            <span class="max-w-20 truncate">{{ auth.user.nickname }}</span>
            <svg
              class="h-3 w-3 transition-transform duration-200"
              :class="userMenuOpen ? 'rotate-180' : ''"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>
          <Transition name="menu">
            <div
              v-if="userMenuOpen"
              class="absolute right-0 z-40 mt-2 w-36 overflow-hidden rounded-xl border border-stone-200 bg-white/95 shadow-lg backdrop-blur-xl dark:border-stone-700 dark:bg-stone-900/95"
            >
              <button
                type="button"
                class="flex w-full items-center gap-2 px-3.5 py-2.5 text-left text-xs text-stone-500 transition-colors hover:bg-stone-100 hover:text-red-500 dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-red-400"
                @click="logout"
              >
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <path d="m16 17 5-5-5-5" />
                  <path d="M21 12H9" />
                </svg>
                {{ t('auth.logout') }}
              </button>
            </div>
          </Transition>
          <!-- 点击菜单外部关闭 -->
          <div
            v-if="userMenuOpen"
            class="fixed inset-0 z-30"
            aria-hidden="true"
            @click="userMenuOpen = false"
          />
        </div>

        <!-- 中英文切换 -->
        <div
          class="flex items-center rounded-full border border-stone-200 bg-stone-100/80 p-0.5 dark:border-stone-700 dark:bg-stone-800/80"
          role="group"
          aria-label="Language"
        >
          <button
            type="button"
            class="rounded-full px-2.5 py-1 text-xs transition-colors"
            :class="
              locale === 'zh'
                ? 'bg-white text-stone-900 shadow-sm dark:bg-stone-700 dark:text-white'
                : 'text-stone-400 hover:text-stone-600 dark:text-stone-500 dark:hover:text-stone-300'
            "
            @click="setLocale('zh')"
          >
            中
          </button>
          <button
            type="button"
            class="rounded-full px-2.5 py-1 text-xs transition-colors"
            :class="
              locale === 'en'
                ? 'bg-white text-stone-900 shadow-sm dark:bg-stone-700 dark:text-white'
                : 'text-stone-400 hover:text-stone-600 dark:text-stone-500 dark:hover:text-stone-300'
            "
            @click="setLocale('en')"
          >
            EN
          </button>
        </div>

        <!-- 明暗切换 -->
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full border border-stone-200 bg-white/80 text-stone-500 shadow-sm backdrop-blur transition-colors hover:border-indigo-300 hover:text-indigo-600 dark:border-stone-700 dark:bg-stone-800/80 dark:text-stone-400 dark:hover:border-amber-300/50 dark:hover:text-amber-300"
          :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <Transition name="theme-icon" mode="out-in">
            <svg
              v-if="theme === 'dark'"
              key="moon"
              class="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
            <svg
              v-else
              key="sun"
              class="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32 1.41-1.41" />
            </svg>
          </Transition>
        </button>

        <!-- 移动端汉堡按钮 -->
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full border border-stone-200 bg-white/80 text-stone-500 shadow-sm backdrop-blur transition-colors hover:border-indigo-300 hover:text-indigo-600 sm:hidden dark:border-stone-700 dark:bg-stone-800/80 dark:text-stone-400 dark:hover:border-amber-300/50 dark:hover:text-amber-300"
          :aria-expanded="menuOpen"
          aria-label="Menu"
          @click="menuOpen = !menuOpen"
        >
          <Transition name="theme-icon" mode="out-in">
            <svg
              v-if="!menuOpen"
              key="menu"
              class="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
            <svg
              v-else
              key="close"
              class="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </Transition>
        </button>
      </div>
    </div>

    <!-- 移动端下拉导航 -->
    <Transition name="menu">
      <nav
        v-if="menuOpen"
        class="border-t border-stone-200/70 bg-white/90 backdrop-blur-xl sm:hidden dark:border-stone-800/70 dark:bg-[#0a0c12]/90"
        aria-label="Mobile"
      >
        <div class="mx-auto flex max-w-4xl flex-col px-4">
          <router-link
            v-for="link in links"
            :key="link.name"
            :to="{ name: link.name }"
            class="flex h-12 items-center text-sm transition-colors"
            :class="
              route.name === link.name
                ? 'font-medium text-indigo-600 dark:text-indigo-400'
                : 'text-stone-500 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100'
            "
          >
            <span
              class="mr-3 h-1 w-1 rounded-full"
              :class="route.name === link.name ? 'bg-indigo-500' : 'bg-stone-300 dark:bg-stone-600'"
              aria-hidden="true"
            />
            {{ link.label }}
          </router-link>

          <!-- 登录 / 用户 -->
          <div class="border-t border-stone-200/70 dark:border-stone-800/70">
            <button
              v-if="!auth.user"
              type="button"
              class="flex h-12 items-center text-sm text-indigo-600 dark:text-indigo-400"
              @click="menuOpen = false; auth.openModal()"
            >
              {{ t('comment.loginBtn') }}
            </button>
            <template v-else>
              <div class="flex h-12 items-center gap-2 text-sm text-stone-600 dark:text-stone-300">
                <span
                  class="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 text-[11px] font-bold text-white"
                  aria-hidden="true"
                >
                  {{ userInitial }}
                </span>
                {{ auth.user.nickname }}
              </div>
              <button
                type="button"
                class="flex h-12 items-center text-sm text-red-500 dark:text-red-400"
                @click="logout"
              >
                {{ t('auth.logout') }}
              </button>
            </template>
          </div>
        </div>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.menu-enter-active,
.menu-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
