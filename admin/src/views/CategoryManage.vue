<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { Category } from '@/types'

const list = ref<Category[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const editing = ref<Category | null>(null)
const form = reactive({ name: '', slug: '', description: '' })

async function load() {
  loading.value = true
  try {
    list.value = await getCategories()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', slug: '', description: '' })
  dialogVisible.value = true
}

function openEdit(row: Category) {
  editing.value = row
  Object.assign(form, { name: row.name, slug: row.slug, description: row.description })
  dialogVisible.value = true
}

async function submit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入分类名')
    return
  }
  try {
    if (editing.value) {
      await updateCategory(editing.value.id, { ...form })
      ElMessage.success('已更新')
    } else {
      await createCategory({ ...form })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

async function handleDelete(row: Category) {
  await ElMessageBox.confirm(
    `删除分类「${row.name}」后其下文章将变为未分类，确定？`,
    '删除确认',
    { type: 'warning' },
  )
  try {
    await deleteCategory(row.id)
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
    <PageHeader title="分类管理" description="管理文章分类，删除分类后其下文章将变为未分类">
      <el-button type="primary" @click="openCreate">新建分类</el-button>
    </PageHeader>

    <el-card shadow="never" class="overflow-hidden">
      <el-table :data="list" v-loading="loading" stripe empty-text="暂无分类，点击右上角「新建分类」">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="slug" label="Slug" width="180" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="post_count" label="文章数" width="90" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '新建分类'" width="480px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" maxlength="50" placeholder="如：技术笔记" />
        </el-form-item>
        <el-form-item label="Slug">
          <el-input v-model="form.slug" maxlength="50" placeholder="留空自动生成" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
