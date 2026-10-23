<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useLocale } from '@/composables/useLocale'

const auth = useAuthStore()
const { t } = useLocale()

type Mode = 'login' | 'register'
const mode = ref<Mode>('login')
const submitting = ref(false)
const message = ref('')
const ok = ref(false)
const form = reactive({ username: '', nickname: '', password: '', confirm: '' })

const isLogin = computed(() => mode.value === 'login')
const title = computed(() => (isLogin.value ? t('auth.titleLogin') : t('auth.titleRegister')))
const submitText = computed(() =>
  isLogin.value ? t('auth.submitLogin') : t('auth.submitRegister'),
)
const switchText = computed(() => (isLogin.value ? t('auth.toRegister') : t('auth.toLogin')))

/** 与输入框一致的样式 */
const field =
  'w-full rounded-xl border border-stone-200 bg-white/60 px-3.5 py-2.5 text-sm text-stone-700 outline-none transition-all placeholder:text-stone-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 dark:border-stone-700 dark:bg-stone-900/60 dark:text-stone-200 dark:focus:border-indigo-500 dark:focus:ring-indigo-500/20'

// 打开弹窗时重置表单与提示
watch(
  () => auth.modalOpen,
  (open) => {
    if (open) {
      mode.value = 'login'
      submitting.value = false
      message.value = ''
      ok.value = false
      form.username = ''
      form.nickname = ''
      form.password = ''
      form.confirm = ''
    }
  },
)

function switchMode() {
  mode.value = isLogin.value ? 'register' : 'login'
  message.value = ''
  ok.value = false
}

function validate(): string {
  if (!form.username.trim()) return t('auth.needUsername')
  if (!isLogin.value) {
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(form.username.trim())) return t('auth.usernameRule')
    if (!form.nickname.trim()) return t('auth.needNickname')
  }
  if (!form.password) return t('auth.needPassword')
  if (!isLogin.value) {
    if (form.password.length < 6) return t('auth.passwordShort')
    if (form.password !== form.confirm) return t('auth.passwordMismatch')
  }
  return ''
}

async function submit() {
  const error = validate()
  if (error) {
    message.value = error
    ok.value = false
    return
  }
  submitting.value = true
  message.value = ''
  try {
    if (isLogin.value) {
      await auth.login(form.username.trim(), form.password)
    } else {
      await auth.register({
        username: form.username.trim(),
        nickname: form.nickname.trim(),
        password: form.password,
      })
    }
    auth.closeModal()
  } catch (e) {
    message.value = e instanceof Error ? e.message : String(e)
    ok.value = false
  } finally {
    submitting.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') auth.closeModal()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="auth-modal">
      <div
        v-if="auth.modalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @keydown="onKeydown"
      >
        <!-- 背景遮罩 -->
        <div
          class="absolute inset-0 bg-stone-950/40 backdrop-blur-sm"
          @click="auth.closeModal"
        />

        <div
          role="dialog"
          aria-modal="true"
          class="glass-card relative w-full max-w-sm overflow-hidden rounded-2xl p-6 shadow-2xl sm:p-7"
        >
          <span
            class="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400"
            aria-hidden="true"
          />

          <div class="mb-6 flex items-start justify-between">
            <h2 class="font-mono text-lg font-bold tracking-tight text-stone-900 dark:text-stone-100">
              {{ title }}
            </h2>
            <button
              type="button"
              class="flex h-7 w-7 items-center justify-center rounded-full text-stone-400 transition-colors hover:bg-stone-200/70 hover:text-stone-600 dark:hover:bg-stone-700/70 dark:hover:text-stone-300"
              :aria-label="t('comment.cancel')"
              @click="auth.closeModal"
            >
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form class="space-y-3.5" @submit.prevent="submit">
            <input
              v-model="form.username"
              :placeholder="t('auth.username')"
              maxlength="20"
              autocomplete="username"
              :class="field"
            />
            <template v-if="!isLogin">
              <input
                v-model="form.nickname"
                :placeholder="t('auth.nickname')"
                maxlength="20"
                autocomplete="nickname"
                :class="field"
              />
            </template>
            <input
              v-model="form.password"
              type="password"
              :placeholder="t('auth.password')"
              maxlength="64"
              :autocomplete="isLogin ? 'current-password' : 'new-password'"
              :class="field"
            />
            <template v-if="!isLogin">
              <input
                v-model="form.confirm"
                type="password"
                :placeholder="t('auth.confirmPassword')"
                maxlength="64"
                autocomplete="new-password"
                :class="field"
              />
            </template>

            <p class="min-h-4 text-xs" :class="ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'">
              {{ message }}
            </p>

            <button
              type="submit"
              :disabled="submitting"
              class="w-full rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-2.5 text-sm font-medium text-white shadow-md shadow-indigo-500/30 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/40 active:translate-y-0 disabled:translate-y-0 disabled:opacity-50"
            >
              {{ submitting ? t('comment.submitting') : submitText }}
            </button>

            <button
              type="button"
              class="block w-full pt-1 text-center text-xs text-stone-400 transition-colors hover:text-indigo-500 dark:text-stone-500 dark:hover:text-indigo-400"
              @click="switchMode"
            >
              {{ switchText }}
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.auth-modal-enter-active,
.auth-modal-leave-active {
  transition: opacity 0.2s ease;
}
.auth-modal-enter-active .glass-card,
.auth-modal-leave-active .glass-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.auth-modal-enter-from,
.auth-modal-leave-to {
  opacity: 0;
}
.auth-modal-enter-from .glass-card,
.auth-modal-leave-to .glass-card {
  transform: translateY(10px) scale(0.97);
  opacity: 0;
}
</style>
