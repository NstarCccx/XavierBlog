<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowRight,
  ChatDotRound,
  Collection,
  Document,
  TrendCharts,
  View,
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getDashboardStats } from '@/api'
import { errorMessage } from '@/api/http'
import type { DashboardStats } from '@/types'

const ViewsChart = defineAsyncComponent(() => import('@/components/ViewsChart.vue'))
const router = useRouter()

const stats = ref<DashboardStats | null>(null)
const loading = ref(false)

const cards = computed(() => [
  {
    label: '文章总数',
    value: stats.value?.post_count ?? 0,
    hint: `已发布 ${stats.value?.published_count ?? 0} 篇 · 草稿 ${stats.value?.draft_count ?? 0} 篇`,
    icon: Document,
    tone: 'bg-indigo-50 text-indigo-500',
    to: '/posts',
  },
  {
    label: '评论总数',
    value: stats.value?.comment_count ?? 0,
    hint: `待审核 ${stats.value?.pending_comment_count ?? 0} 条`,
    icon: ChatDotRound,
    tone: 'bg-emerald-50 text-emerald-500',
    to: '/comments',
  },
  {
    label: '总浏览量',
    value: stats.value?.total_views ?? 0,
    hint: '点击查看各文章浏览明细',
    icon: View,
    tone: 'bg-amber-50 text-amber-500',
    to: '/posts',
  },
  {
    label: '分类数',
    value: stats.value?.category_count ?? 0,
    hint: `共 ${stats.value?.tag_count ?? 0} 个标签`,
    icon: Collection,
    tone: 'bg-sky-50 text-sky-500',
    to: '/categories',
  },
])

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await getDashboardStats()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <PageHeader title="仪表盘" description="Blog数据概览" />

    <div v-loading="loading" class="min-h-32">
      <template v-if="stats">
        <!-- 文章浏览量图表 -->
        <el-card shadow="never" class="overflow-hidden">
          <div class="mb-2 flex items-center gap-2 text-sm font-semibold text-gray-800">
            <el-icon class="text-indigo-500"><TrendCharts /></el-icon>
            文章浏览量 TOP 10
          </div>
          <ViewsChart v-if="stats.top_views.length" :items="stats.top_views" />
          <div v-else class="py-14 text-center text-sm text-gray-400">还没有文章浏览数据</div>
        </el-card>

        <!-- 统计卡片（整卡可点击跳转） -->
        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <el-card
            v-for="card in cards"
            :key="card.label"
            shadow="never"
            class="group cursor-pointer transition hover:shadow-md!"
            @click="router.push(card.to)"
          >
            <div class="flex items-center gap-3">
              <span
                class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl"
                :class="card.tone"
              >
                <el-icon :size="20"><component :is="card.icon" /></el-icon>
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-sm text-gray-500">{{ card.label }}</p>
                <p class="text-2xl font-bold text-gray-900">{{ card.value }}</p>
              </div>
              <el-icon
                class="text-gray-300 opacity-0 transition group-hover:translate-x-0.5 group-hover:opacity-100"
              >
                <ArrowRight />
              </el-icon>
            </div>
            <p class="mt-3 truncate text-xs text-gray-400">{{ card.hint }}</p>
          </el-card>
        </div>

        <!-- 汇总条 -->
        <el-card shadow="never" class="mt-4">
          <div class="flex flex-wrap items-center gap-x-8 gap-y-2 text-sm text-gray-500">
            <span>草稿 <span class="font-semibold text-gray-800">{{ stats.draft_count }}</span> 篇</span>
            <span>已发布 <span class="font-semibold text-gray-800">{{ stats.published_count }}</span> 篇</span>
            <span>标签 <span class="font-semibold text-gray-800">{{ stats.tag_count }}</span> 个</span>
            <span>待审评论 <span class="font-semibold text-amber-500">{{ stats.pending_comment_count }}</span> 条</span>
          </div>
        </el-card>
      </template>

      <el-card v-else-if="!loading" shadow="never">
        <p class="py-6 text-center text-sm text-gray-400">统计数据加载失败，请刷新重试</p>
      </el-card>
    </div>
  </div>
</template>
