<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import type { ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getPost, createPost, updatePost, getCategories, getTags } from '@/api'
import { errorMessage, http } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'
import type { PostForm } from '@/types'

const route = useRoute()
const router = useRouter()
const postId = computed(() => (route.params.id ? Number(route.params.id) : null))

const form = ref<PostForm>({
  title: '',
  slug: '',
  summary: '',
  content: '',
  cover: '',
  status: 'draft',
  is_pinned: false,
  category_id: null,
  tag_ids: [],
})

const categories = ref<{ id: number; name: string }[]>([])
const allTags = ref<{ id: number; name: string }[]>([])
const saving = ref(false)

const toolbars: ToolbarNames[] = [
  'bold', 'italic', 'strikeThrough', '-',
  'title', 'quote', 'unorderedList', 'orderedList', '-',
  'code', 'codeRow', 'link', 'image', 'table', '-',
  'revoke', 'next', '=',
  'preview', 'htmlPreview',
]

onMounted(async () => {
  try {
    const [cats, tags] = await Promise.all([getCategories(), getTags()])
    categories.value = cats
    allTags.value = tags

    if (postId.value) {
      const post = await getPost(postId.value)
      form.value = {
        title: post.title,
        slug: post.slug,
        summary: post.summary,
        content: post.content,
        cover: post.cover,
        status: post.status,
        is_pinned: post.is_pinned,
        category_id: post.category?.id ?? null,
        tag_ids: post.tags.map((t) => t.id),
      }
    }
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
})

async function save(targetStatus: 'draft' | 'published') {
  if (!form.value.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!form.value.content.trim()) {
    ElMessage.warning('请输入正文内容')
    return
  }
  saving.value = true
  const payload = { ...form.value, status: targetStatus }
  try {
    if (postId.value) {
      await updatePost(postId.value, payload)
    } else {
      const created = await createPost(payload)
      // 新建后替换路由，避免再保存时重复创建
      router.replace(`/posts/${created.id}/edit`)
    }
    form.value.status = targetStatus
    ElMessage.success(targetStatus === 'published' ? '已发布' : '已保存草稿')
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    saving.value = false
  }
}

/** 编辑器里的图片上传：走后端 /admin/uploads 接口 */
async function onUploadImg(files: File[], callback: (urls: string[]) => void) {
  const urls: string[] = []
  for (const file of files) {
    const data = new FormData()
    data.append('file', file)
    try {
      const resp = await http.post('/admin/uploads', data)
      urls.push(resp.data.url as string)
    } catch (e) {
      ElMessage.error(errorMessage(e))
    }
  }
  callback(urls)
}
</script>

<template>
  <div>
    <PageHeader
      :title="postId ? '编辑文章' : '新建文章'"
      description="支持 Markdown，正文里的图片可直接上传"
    >
      <el-button @click="router.back()">返回</el-button>
      <el-button :disabled="saving" @click="save('draft')">存草稿</el-button>
      <el-button type="primary" :loading="saving" @click="save('published')">发布</el-button>
    </PageHeader>

    <el-card shadow="never">
      <el-form label-width="80px" label-position="left">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="文章标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="2"
            placeholder="展示在列表页的摘要（留空自动截取）"
            maxlength="500"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable style="width: 220px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签" style="width: 100%" filterable>
            <el-option v-for="t in allTags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" active-text="置顶显示在文章列表最前" />
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="form.cover" placeholder="封面图 URL（可在图片库复制）" />
        </el-form-item>
      </el-form>

      <MdEditor
        v-model="form.content"
        :toolbars="toolbars"
        editor-id="post-editor"
        placeholder="开始写吧…（支持 Markdown）"
        :style="{ height: '520px' }"
        @on-upload-img="onUploadImg"
      />
    </el-card>
  </div>
</template>
