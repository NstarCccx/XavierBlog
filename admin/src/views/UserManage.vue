<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Key, Search } from '@element-plus/icons-vue'
import { getUsers, resetUserPassword } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { UserAdmin } from '@/types'

const list = ref<UserAdmin[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const keyword = ref('')

const resetDialogVisible = ref(false)
const resetTarget = ref<UserAdmin | null>(null)
const pwdForm = reactive({ password: '', confirm: '' })

async function load() {
  loading.value = true
  try {
    const result = await getUsers({
      page: page.value,
      page_size: pageSize,
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

function search() {
  page.value = 1
  load()
}

function openReset(row: UserAdmin) {
  resetTarget.value = row
  pwdForm.password = ''
  pwdForm.confirm = ''
  resetDialogVisible.value = true
}

async function submitReset() {
  if (!resetTarget.value) return
  if (pwdForm.password.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (pwdForm.password !== pwdForm.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  try {
    await resetUserPassword(resetTarget.value.id, pwdForm.password)
    ElMessage.success(`已重置 ${resetTarget.value.username} 的密码`)
    resetDialogVisible.value = false
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
    <PageHeader title="用户管理" description="管理注册用户、重置登录密码" />

    <el-card shadow="never" class="overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 px-5 pb-4 pt-5">
        <el-input
          v-model="keyword"
          placeholder="搜索用户名或昵称"
          clearable
          style="width: 220px"
          @keyup.enter="search"
          @clear="search"
        />
        <el-button type="primary" :icon="Search" @click="search">搜索</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe empty-text="暂无用户">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="nickname" label="昵称" min-width="140" show-overflow-tooltip />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Key" @click="openReset(row)">重置密码</el-button>
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

    <el-dialog v-model="resetDialogVisible" title="重置密码" width="420px">
      <p class="mb-3 text-sm text-gray-500">
        为用户 <span class="font-medium text-gray-700">{{ resetTarget?.username }}</span>（{{ resetTarget?.nickname }}）设置新密码：
      </p>
      <el-form label-width="90px">
        <el-form-item label="新密码">
          <el-input
            v-model="pwdForm.password"
            type="password"
            show-password
            maxlength="64"
            placeholder="至少 6 位"
            @keyup.enter="submitReset"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="pwdForm.confirm"
            type="password"
            show-password
            maxlength="64"
            @keyup.enter="submitReset"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReset">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>
