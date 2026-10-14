<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, CopyDocument, Delete, Picture } from '@element-plus/icons-vue'
import { getUploads, deleteUpload } from '@/api'
import { errorMessage, http } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { UploadItem } from '@/types'

const list = ref<UploadItem[]>([])
const loading = ref(false)
const uploading = ref(false)
const inputRef = ref<HTMLInputElement>()

async function load() {
  loading.value = true
  try {
    list.value = await getUploads()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

async function handleFiles(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  uploading.value = true
  try {
    for (const file of Array.from(input.files)) {
      const data = new FormData()
      data.append('file', file)
      await http.post('/admin/uploads', data)
    }
    ElMessage.success('上传完成')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function copyUrl(item: UploadItem) {
  const full = `${location.origin}${item.url}`
  try {
    await navigator.clipboard.writeText(full)
    ElMessage.success('已复制完整链接')
  } catch {
    ElMessage.warning(`复制失败，链接：${full}`)
  }
}

async function handleDelete(item: UploadItem) {
  await ElMessageBox.confirm(`删除图片 ${item.filename}？`, '删除确认', { type: 'warning' })
  try {
    await deleteUpload(item.url)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

function formatSize(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

onMounted(load)
</script>

<template>
  <div>
    <PageHeader title="图片库" description="上传并管理文章配图，复制链接后可粘贴到编辑器或封面地址栏">
      <input
        ref="inputRef"
        type="file"
        accept=".jpg,.jpeg,.png,.gif,.webp,.svg"
        multiple
        hidden
        @change="handleFiles"
      />
      <el-button type="primary" :icon="Plus" :loading="uploading" @click="inputRef?.click()">
        上传图片
      </el-button>
    </PageHeader>

    <el-card v-loading="loading" shadow="never">
      <div
        v-if="!list.length"
        class="flex flex-col items-center justify-center gap-2 py-14 text-gray-400"
      >
        <el-icon :size="40" class="text-gray-300"><Picture /></el-icon>
        <p class="text-sm">还没有图片，点击右上角「上传图片」开始</p>
      </div>
      <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        <div
          v-for="item in list"
          :key="item.url"
          class="group overflow-hidden rounded-lg border border-gray-200 bg-white transition-shadow hover:shadow-md"
        >
          <div class="flex h-36 items-center justify-center overflow-hidden bg-gray-50">
            <img :src="item.url" :alt="item.filename" class="max-h-full max-w-full object-contain" />
          </div>
          <div class="p-2">
            <p class="truncate text-xs text-gray-600" :title="item.filename">{{ item.filename }}</p>
            <p class="text-xs text-gray-400">{{ formatSize(item.size) }}</p>
            <div class="mt-1 flex gap-1">
              <el-button size="small" text type="primary" :icon="CopyDocument" @click="copyUrl(item)">
                链接
              </el-button>
              <el-button size="small" text type="danger" :icon="Delete" @click="handleDelete(item)">
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>
