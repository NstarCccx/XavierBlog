<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSiteStore } from '@/stores/site'
import { renderMarkdown } from '@/utils/markdown'
import { useLocale } from '@/composables/useLocale'

const site = useSiteStore()
const { t } = useLocale()
onMounted(site.load)

const raw = computed(() => site.info.about_content || t('about.empty'))

/** 第一个一级标题作为名字（页头显示 About·名字） */
const name = computed(() => raw.value.match(/^\s*#\s+(.+?)\s*$/m)?.[1] ?? '')

/** 正文去掉第一个一级标题，避免与页头重复 */
const html = computed(() =>
  renderMarkdown(name.value ? raw.value.replace(/^\s*#\s+.+\s*$/m, '') : raw.value).html,
)

const title = computed(() => (name.value ? `${t('about.title')} · ${name.value}` : t('about.title')))
</script>

<template>
  <div class="px-4 py-10">
    <!-- 页头：左对齐的 About·名字 标题 -->
    <header class="mb-10">
      <h1
        class="bg-gradient-to-r from-indigo-600 via-violet-600 to-cyan-500 bg-clip-text text-left text-3xl font-bold tracking-tight text-transparent sm:text-4xl dark:from-indigo-400 dark:via-violet-400 dark:to-cyan-300"
      >
        {{ title }}
      </h1>
    </header>

    <!-- 正文卡片：顶部渐变装饰条 + 玻璃卡片 -->
    <article class="glass-card relative overflow-hidden p-6 sm:p-8">
      <span
        class="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400 opacity-70"
        aria-hidden="true"
      />
      <div class="markdown-body about-md" v-html="html" />
    </article>
  </div>
</template>

<style scoped>
/* 关于页 Markdown 排版：等宽符号前缀 + 主题色点缀（覆盖全局 .markdown-body 的部分样式） */

.about-md :deep(h2) {
  margin: 1.75rem 0 0.75rem;
  padding-bottom: 0;
  border-bottom: none;
}
.about-md :deep(h2::before) {
  content: '##';
  margin-right: 0.6rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.75em;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: rgb(99 102 241 / 0.55);
}
.about-md :deep(h3::before) {
  content: '###';
  margin-right: 0.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.7em;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: rgb(168 162 158 / 0.8);
}
.dark .about-md :deep(h2::before) {
  color: rgb(129 140 248 / 0.6);
}

/* 强调文字用主题靛蓝，列表符号同色 */
.about-md :deep(strong) {
  color: #4338ca;
}
.dark .about-md :deep(strong) {
  color: #a5b4fc;
}
.about-md :deep(li::marker) {
  color: #818cf8;
}

/* 引用块：渐变左边条 + 淡靛蓝底 */
.about-md :deep(blockquote) {
  border-left: 3px solid transparent;
  border-image: linear-gradient(to bottom, #6366f1, #a855f7) 1;
  background: rgb(99 102 241 / 0.06);
  border-radius: 0 0.5rem 0.5rem 0;
}
.dark .about-md :deep(blockquote) {
  background: rgb(99 102 241 / 0.1);
}

/* 分隔线：居中渐隐，呼应全站装饰线 */
.about-md :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, rgb(99 102 241 / 0.5), transparent);
}

/* 图片居中 + 投影 */
.about-md :deep(img) {
  display: block;
  margin-inline: auto;
  border-radius: 0.75rem;
  box-shadow: 0 10px 30px rgb(0 0 0 / 0.12);
}
.dark .about-md :deep(img) {
  box-shadow: 0 10px 30px rgb(0 0 0 / 0.5);
}
</style>
