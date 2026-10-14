<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSiteConfig, updateSiteConfig, changePassword } from '@/api'
import { errorMessage } from '@/api/http'
import PageHeader from '@/components/PageHeader.vue'

// ---------- 站点设置 ----------
const siteForm = reactive({
  site_name: '',
  site_description: '',
  footer: '',
  about_content: '',
})
const siteSaving = ref(false)

async function loadSite() {
  try {
    const config = await getSiteConfig()
    Object.assign(siteForm, config)
  } catch (e) {
    ElMessage.error(errorMessage(e))
  }
}

async function saveSite() {
  siteSaving.value = true
  try {
    await updateSiteConfig({ ...siteForm })
    ElMessage.success('站点设置已保存')
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    siteSaving.value = false
  }
}

// ---------- 修改密码 ----------
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const pwdSaving = ref(false)

async function savePassword() {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写完整')
    return
  }
  if (pwdForm.newPassword.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdSaving.value = true
  try {
    await changePassword(pwdForm.oldPassword, pwdForm.newPassword)
    ElMessage.success('密码已修改，请重新登录')
    localStorage.removeItem('admin_token')
    location.href = '/login'
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    pwdSaving.value = false
  }
}

onMounted(loadSite)
</script>

<template>
  <div>
    <PageHeader title="站点设置" />

    <el-card shadow="never" class="mb-5">
      <template #header><span class="font-semibold">基本信息</span></template>
      <el-form :model="siteForm" label-width="90px">
        <el-form-item label="站点名称">
          <el-input v-model="siteForm.site_name" maxlength="50" />
        </el-form-item>
        <el-form-item label="站点简介">
          <el-input v-model="siteForm.site_description" type="textarea" :rows="2" maxlength="200" />
        </el-form-item>
        <el-form-item label="页脚文字">
          <el-input v-model="siteForm.footer" maxlength="200" />
        </el-form-item>
        <el-form-item label="关于页内容">
          <el-input
            v-model="siteForm.about_content"
            type="textarea"
            :rows="8"
            placeholder="支持 Markdown"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="siteSaving" @click="saveSite">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <template #header><span class="font-semibold">修改密码</span></template>
      <el-form :model="pwdForm" label-width="90px" style="max-width: 420px">
        <el-form-item label="原密码">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password @keyup.enter="savePassword" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="pwdSaving" @click="savePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>
