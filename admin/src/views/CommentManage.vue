<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getComments, approveComment, rejectComment, deleteComment, replyComment } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { CommentAdmin } from '@/types'

const list = ref<CommentAdmin[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const status = ref('')
const keyword = ref('')

const replyDialogVisible = ref(false)
const replyTarget = ref<CommentAdmin | null>(null)
const replyContent = ref('')

async function load() {
  loading.value = true
  try {
    const result = await getComments({
      page: page.value,
      page_size: pageSize,
      status: status.value || undefined,
      keyword: keyword.value || undefined,
    })
    list.value = result.items
    total.value = result.total
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

async function handleApprove(row: CommentAdmin) {
  try {
    await approveComment(row.id)
    ElMessage.success('已通过')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

async function handleReject(row: CommentAdmin) {
  try {
    await rejectComment(row.id)
    ElMessage.success('已退回待审核')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

async function handleDelete(row: CommentAdmin) {
  await ElMessageBox.confirm('删除该评论（其下回复一并删除）？', '删除确认', { type: 'warning' })
  try {
    await deleteComment(row.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

function openReply(row: CommentAdmin) {
  replyTarget.value = row
  replyContent.value = ''
  replyDialogVisible.value = true
}

async function submitReply() {
  if (!replyTarget.value || !replyContent.value.trim()) return
  try {
    await replyComment(replyTarget.value.id, replyContent.value.trim())
    ElMessage.success('回复成功')
    replyDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(load)
</script>

<template>
  <div>
    <PageHeader title="评论管理" description="审核游客留言、回复评论" />

    <el-card shadow="never" class="overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 px-5 pb-4 pt-5">
        <el-select
          v-model="status"
          placeholder="全部状态"
          clearable
          style="width: 130px"
          @change="page = 1; load()"
        >
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
        </el-select>
        <el-input
          v-model="keyword"
          placeholder="搜索内容或昵称"
          clearable
          style="width: 200px"
          @keyup.enter="page = 1; load()"
          @clear="page = 1; load()"
        />
        <el-button type="primary" @click="page = 1; load()">搜索</el-button>
      </div>

      <el-table
        :data="list"
        v-loading="loading"
        stripe
        :empty-text="status || keyword ? '没有符合条件的评论' : '暂无评论'"
      >
        <el-table-column prop="nickname" label="昵称" width="120">
          <template #default="{ row }">
            {{ row.nickname }}
            <el-tag v-if="row.is_author" size="small" type="primary" class="ml-1">博主</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="post_title" label="所属文章" min-width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : 'warning'" size="small">
              {{ row.status === 'approved' ? '已通过' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" link type="success" @click="handleApprove(row)">通过</el-button>
            <el-button v-if="row.status === 'approved' && !row.is_author" link type="warning" @click="handleReject(row)">退回</el-button>
            <el-button link type="primary" @click="openReply(row)">回复</el-button>
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

    <el-dialog v-model="replyDialogVisible" title="回复评论" width="520px">
      <p class="mb-2 text-sm text-gray-500">
        回复 {{ replyTarget?.nickname }}：{{ replyTarget?.content }}
      </p>
      <el-input
        v-model="replyContent"
        type="textarea"
        :rows="3"
        maxlength="2000"
        placeholder="以博主身份回复（发布后前台直接可见）"
      />
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply">回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>
