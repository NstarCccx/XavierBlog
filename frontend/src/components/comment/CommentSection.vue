<script setup lang="ts">
import { computed, ref } from 'vue'
import { createComment, getPostComments } from '@/api/blog'
import { useAuthStore } from '@/stores/auth'
import { useLocale } from '@/composables/useLocale'
import type { Comment } from '@/types'
import CommentItem from './CommentItem.vue'

const props = defineProps<{ postId: number }>()

const { t } = useLocale()
const auth = useAuthStore()

const comments = ref<Comment[]>([])
const submitting = ref(false)
const message = ref('')
const ok = ref(false)
const content = ref('')
const replyTo = ref<Comment | null>(null)

const userInitial = computed(
  () => (auth.user?.nickname || auth.user?.username || '?').trim().charAt(0).toUpperCase(),
)

/** 评论总数（含楼中楼回复） */
const total = computed(() => {
  const count = (list: Comment[]): number =>
    list.reduce((n, c) => n + 1 + count(c.replies ?? []), 0)
  return count(comments.value)
})

/** 输入框统一样式：聚焦时渐变光环 */
const field =
  'w-full rounded-xl border border-stone-200 bg-white/60 px-3.5 py-2.5 text-sm text-stone-700 outline-none transition-all placeholder:text-stone-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 dark:border-stone-700 dark:bg-stone-900/60 dark:text-stone-200 dark:focus:border-indigo-500 dark:focus:ring-indigo-500/20'

async function load() {
  comments.value = await getPostComments(props.postId)
}

async function submit() {
  if (!content.value.trim()) {
    message.value = t('comment.needContent')
    ok.value = false
    return
  }
  submitting.value = true
  message.value = ''
  try {
    await createComment({
      post_id: props.postId,
      parent_id: replyTo.value?.id ?? null,
      content: content.value.trim(),
    })
    content.value = ''
    replyTo.value = null
    message.value = t('comment.ok')
    ok.value = true
    await load()
  } catch (e) {
    message.value = e instanceof Error ? e.message : t('comment.needContent')
    ok.value = false
  } finally {
    submitting.value = false
  }
}

load()
</script>

<template>
  <section>
    <h2
      class="mb-6 flex items-center gap-3 font-mono text-sm font-semibold tracking-widest text-stone-500 uppercase dark:text-stone-400"
    >
      <span class="h-px w-10 bg-indigo-400/50 dark:bg-indigo-500/40" aria-hidden="true" />
      {{ t('comment.title', { n: total }) }}
      <span
        class="h-px flex-1 bg-gradient-to-r from-indigo-400/40 to-transparent dark:from-indigo-500/30"
        aria-hidden="true"
      />
    </h2>

    <!-- 未登录：提示登录 -->
    <div
      v-if="!auth.user"
      class="glass-card relative mb-8 flex flex-wrap items-center justify-between gap-3 overflow-hidden p-5 sm:p-6"
    >
      <span
        class="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400 opacity-70"
        aria-hidden="true"
      />
      <p class="text-sm text-stone-500 dark:text-stone-400">
        {{ t('comment.loginPrompt') }}
      </p>
      <button
        type="button"
        class="rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-2 text-sm text-white shadow-md shadow-indigo-500/30 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/40 active:translate-y-0"
        @click="auth.openModal()"
      >
        {{ t('comment.loginBtn') }}
      </button>
    </div>

    <!-- 已登录：输入区 -->
    <form v-else class="glass-card relative mb-8 overflow-hidden p-5 sm:p-6" @submit.prevent="submit">
      <span
        class="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400 opacity-70"
        aria-hidden="true"
      />

      <p
        v-if="replyTo"
        class="mb-4 inline-flex items-center gap-2 rounded-full bg-indigo-50 py-1 pr-2 pl-3 text-sm text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400"
      >
        <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 17H6a4 4 0 0 1-4-4V6a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v7a4 4 0 0 1-4 4h-4l-4 4v-4z" transform="scale(-1,1) translate(-24,0)" />
        </svg>
        {{ t('comment.replyTo', { name: replyTo.nickname }) }}
        <button
          type="button"
          class="rounded-full px-2 py-0.5 text-xs text-stone-400 transition-colors hover:bg-stone-200/70 hover:text-stone-600 dark:hover:bg-stone-700/70 dark:hover:text-stone-300"
          @click="replyTo = null"
        >
          {{ t('comment.cancel') }}
        </button>
      </p>

      <p class="mb-3 flex items-center gap-2 text-xs text-stone-400 dark:text-stone-500">
        <span
          class="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 text-[10px] font-bold text-white"
          aria-hidden="true"
        >
          {{ userInitial }}
        </span>
        {{ t('comment.welcome', { name: auth.user?.nickname }) }}
      </p>

      <textarea v-model="content" rows="4" :placeholder="t('comment.content')" maxlength="2000" :class="field" class="mb-3 resize-y" />

      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs" :class="ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'">
          {{ message }}
        </p>
        <div class="flex items-center gap-4">
          <span class="font-mono text-xs text-stone-300 dark:text-stone-600">{{ content.length }} / 2000</span>
          <button
            type="submit"
            :disabled="submitting"
            class="rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-2 text-sm text-white shadow-md shadow-indigo-500/30 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/40 active:translate-y-0 disabled:translate-y-0 disabled:opacity-50"
          >
            {{ submitting ? t('comment.submitting') : t('comment.submit') }}
          </button>
        </div>
      </div>
    </form>

    <!-- 评论列表 -->
    <div
      v-if="!comments.length"
      class="rounded-2xl border border-dashed border-stone-300 py-12 text-center text-sm text-stone-400 dark:border-stone-700 dark:text-stone-500"
    >
      {{ t('comment.empty') }}
    </div>
    <div v-else class="space-y-4">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @reply="replyTo = $event"
      />
    </div>
  </section>
</template>
