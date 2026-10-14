<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTags, createTag, updateTag, deleteTag } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { Tag } from '@/types'

const list = ref<Tag[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const editing = ref<Tag | null>(null)
const form = reactive({ name: '', slug: '' })

async function load() {
  loading.value = true
  try {
    list.value = await getTags()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', slug: '' })
  dialogVisible.value = true
}

function openEdit(row: Tag) {
  editing.value = row
  Object.assign(form, { name: row.name, slug: row.slug })
  dialogVisible.value = true
}

async function submit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入标签名')
    return
  }
  try {
    if (editing.value) {
      await updateTag(editing.value.id, { ...form })
      ElMessage.success('已更新')
    } else {
      await createTag({ ...form })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

async function handleDelete(row: Tag) {
  await ElMessageBox.confirm(`删除标签「${row.name}」？`, '删除确认', { type: 'warning' })
  try {
    await deleteTag(row.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

onMounted(load)
</script>

<template>
  <div>
    <PageHeader title="标签管理" description="管理文章标签，用于文章多对多归类">
      <el-button type="primary" @click="openCreate">新建标签</el-button>
    </PageHeader>

    <el-card shadow="never" class="overflow-hidden">
      <el-table :data="list" v-loading="loading" stripe empty-text="暂无标签，点击右上角「新建标签」">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="slug" label="Slug" width="180" />
        <el-table-column prop="post_count" label="文章数" width="90" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑标签' : '新建标签'" width="420px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" maxlength="50" placeholder="如：FastAPI" @keyup.enter="submit" />
        </el-form-item>
        <el-form-item label="Slug">
          <el-input v-model="form.slug" maxlength="50" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
