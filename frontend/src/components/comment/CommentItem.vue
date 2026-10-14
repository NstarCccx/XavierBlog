<script setup lang="ts">
import type { Comment } from '@/types'
import { formatDateTime } from '@/utils/format'
import { useLocale } from '@/composables/useLocale'

const props = defineProps<{ comment: Comment }>()

const emit = defineEmits<{ reply: [comment: Comment] }>()

const { t } = useLocale()

/** 依据昵称哈希稳定地取一个渐变头像底色，同一昵称颜色不变 */
const GRADIENTS = [
  'from-indigo-500 to-violet-500',
  'from-sky-500 to-cyan-400',
  'from-rose-500 to-pink-500',
  'from-amber-500 to-orange-400',
  'from-emerald-500 to-teal-400',
  'from-fuchsia-500 to-purple-500',
]

function hashCode(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0
  return Math.abs(h)
}

const gradient = GRADIENTS[hashCode(props.comment.nickname) % GRADIENTS.length]
const initial = props.comment.nickname.trim().charAt(0).toUpperCase() || '?'
</script>

<template>
  <div class="glass-card p-4 sm:p-5">
    <div class="flex items-start gap-3">
      <!-- 渐变头像：昵称首字符 -->
      <span
        class="flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-full bg-gradient-to-br text-sm font-bold text-white shadow-sm"
        :class="gradient"
        aria-hidden="true"
      >
        {{ initial }}
      </span>

      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span
            class="text-sm font-medium"
            :class="comment.is_author ? 'text-indigo-600 dark:text-indigo-400' : 'text-stone-700 dark:text-stone-200'"
          >
            {{ comment.nickname }}
          </span>
          <span
            v-if="comment.is_author"
            class="rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 px-2 py-0.5 text-[11px] font-medium text-white shadow-sm"
          >
            {{ t('comment.author') }}
          </span>
          <span class="font-mono text-xs text-stone-400 dark:text-stone-500">
            {{ formatDateTime(comment.created_at) }}
          </span>
          <button
            class="ml-auto text-xs text-stone-400 transition-colors hover:text-indigo-500 dark:text-stone-500 dark:hover:text-indigo-400"
            @click="emit('reply', comment)"
          >
            {{ t('comment.reply') }}
          </button>
        </div>

        <p class="mt-2 text-sm whitespace-pre-wrap text-stone-600 dark:text-stone-300">
          {{ comment.content }}
        </p>

        <!-- 楼中楼：与头像对齐缩进，渐变竖线 -->
        <div
          v-if="comment.replies.length"
          class="mt-4 space-y-3 border-l-2 border-indigo-200/70 pl-4 dark:border-indigo-500/20"
        >
          <CommentItem
            v-for="reply in comment.replies"
            :key="reply.id"
            :comment="reply"
            @reply="emit('reply', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
