<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPosts, deletePost } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { PostBrief } from '@/types'

const router = useRouter()

const posts = ref<PostBrief[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const status = ref('')
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const result = await getPosts({
      page: page.value,
      page_size: pageSize,
      status: status.value || undefined,
      keyword: keyword.value || undefined,
    })
    posts.value = result.items
    total.value = result.total
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

async function handleDelete(post: PostBrief) {
  await ElMessageBox.confirm(`确定删除「${post.title}」？该操作不可恢复。`, '删除确认', {
    type: 'warning',
  })
  try {
    await deletePost(post.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

function formatTime(value: string | null) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '—'
}

onMounted(load)
</script>

<template>
  <div>
    <PageHeader title="文章管理" description="撰写、发布与管理博客文章">
      <el-button type="success" @click="router.push({ name: 'post-new' })">写文章</el-button>
    </PageHeader>

    <el-card shadow="never" class="overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 px-5 pb-4 pt-5">
        <el-select
          v-model="status"
          placeholder="全部状态"
          clearable
          style="width: 130px"
          @change="page = 1; load()"
        >
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>
        <el-input
          v-model="keyword"
          placeholder="按标题搜索"
          clearable
          style="width: 220px"
          @keyup.enter="page = 1; load()"
          @clear="page = 1; load()"
        />
        <el-button type="primary" @click="page = 1; load()">搜索</el-button>
      </div>

      <el-table
        :data="posts"
        v-loading="loading"
        stripe
        :empty-text="status || keyword ? '没有符合条件的文章' : '暂无文章，点击右上角「写文章」开始创作'"
      >
        <el-table-column prop="title" label="标题" min-width="240">
          <template #default="{ row }">
            <router-link :to="`/posts/${row.id}/edit`" class="text-blue-600 hover:underline">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="110">
          <template #default="{ row }">{{ row.category?.name ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="标签" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag.id" size="small" class="mr-1">{{ tag.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览" width="70" />
        <el-table-column label="发布时间" width="160">
          <template #default="{ row }">{{ formatTime(row.published_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/posts/${row.id}/edit`)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-end border-t border-gray-100 px-5 py-3">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </el-card>
  </div>
</template>
