<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { errorMessage } from '@/api/http'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = ref({ username: '', password: '' })
const loading = ref(false)

async function submit() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || '/')
  } catch (e) {
    ElMessage.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-bg relative flex min-h-screen items-center justify-center overflow-hidden">
    <!-- 网格 + 光斑装饰层 -->
    <div class="grid-overlay absolute inset-0" aria-hidden="true" />
    <div
      class="orb orb-a absolute -left-32 top-1/4 h-96 w-96 rounded-full bg-indigo-600/25 blur-3xl"
      aria-hidden="true"
    />
    <div
      class="orb orb-b absolute -right-24 bottom-1/4 h-80 w-80 rounded-full bg-cyan-500/20 blur-3xl"
      aria-hidden="true"
    />

    <div class="glass-card relative w-[380px] rounded-2xl px-8 pb-8 pt-10">
      <!-- HUD 边角 -->
      <span aria-hidden="true" class="absolute left-0 top-0 h-4 w-4 border-l-2 border-t-2 border-cyan-400/60" />
      <span aria-hidden="true" class="absolute right-0 top-0 h-4 w-4 border-r-2 border-t-2 border-cyan-400/60" />
      <span aria-hidden="true" class="absolute bottom-0 left-0 h-4 w-4 border-b-2 border-l-2 border-cyan-400/60" />
      <span aria-hidden="true" class="absolute bottom-0 right-0 h-4 w-4 border-b-2 border-r-2 border-cyan-400/60" />

      <div class="flex flex-col items-center">
        <span
          class="logo flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 font-mono text-xl font-bold text-white"
        >
          X
        </span>
        <p class="mt-5 font-mono text-[10px] uppercase tracking-[0.35em] text-cyan-300/80">Admin Console</p>
        <h1 class="mt-1.5 text-lg font-bold text-slate-100">XavierBlog</h1>
      </div>

      <div class="my-6 h-px bg-gradient-to-r from-transparent via-indigo-400/40 to-transparent" />

      <el-form :model="form" @submit.prevent="submit">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="w-full" :loading="loading" @click="submit">
          登 录
        </el-button>
      </el-form>

      <p class="mt-6 text-center font-mono text-[10px] tracking-[0.2em] text-slate-600">
      SECURE ACCESS
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-bg {
  background:
    radial-gradient(ellipse 60% 50% at 50% 40%, rgba(79, 70, 229, 0.18), transparent 70%),
    #05080f;
}

.grid-overlay {
  background-image:
    linear-gradient(rgba(129, 140, 248, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(129, 140, 248, 0.08) 1px, transparent 1px);
  background-size: 44px 44px;
  -webkit-mask-image: radial-gradient(ellipse 75% 65% at 50% 45%, black 25%, transparent 78%);
  mask-image: radial-gradient(ellipse 75% 65% at 50% 45%, black 25%, transparent 78%);
}

.glass-card {
  background: rgba(13, 20, 38, 0.6);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(129, 140, 248, 0.2);
  box-shadow:
    0 24px 64px rgba(2, 6, 23, 0.65),
    0 0 90px rgba(99, 102, 241, 0.14);
}

.logo {
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.45);
  animation: pulse-ring 2.6s ease-out infinite;
}

.orb-a {
  animation: drift 14s ease-in-out infinite;
}
.orb-b {
  animation: drift 18s ease-in-out infinite reverse;
}

@keyframes drift {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(36px, -24px) scale(1.08);
  }
}

@keyframes pulse-ring {
  0% {
    box-shadow:
      0 8px 24px rgba(99, 102, 241, 0.45),
      0 0 0 0 rgba(129, 140, 248, 0.4);
  }
  70%,
  100% {
    box-shadow:
      0 8px 24px rgba(99, 102, 241, 0.45),
      0 0 0 12px rgba(129, 140, 248, 0);
  }
}

/* Element Plus 暗色输入适配（仅本页生效） */
:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.28) inset;
  border-radius: 10px;
  transition: box-shadow 0.2s ease;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(129, 140, 248, 0.55) inset;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.9) inset,
    0 0 14px rgba(99, 102, 241, 0.28);
}
:deep(.el-input__inner) {
  color: #e2e8f0;
  caret-color: #818cf8;
}
:deep(.el-input__inner::placeholder) {
  color: #5b6b85;
}
:deep(.el-input__suffix) {
  color: #64748b;
}

/* 渐变登录按钮 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%);
  border: none;
  box-shadow: 0 8px 22px rgba(99, 102, 241, 0.4);
  transition:
    filter 0.2s ease,
    transform 0.15s ease;
}
:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #818cf8 0%, #8b5cf6 100%);
}
:deep(.el-button--primary:active) {
  transform: translateY(1px);
}

@media (prefers-reduced-motion: reduce) {
  .orb-a,
  .orb-b,
  .logo {
    animation: none;
  }
}
</style>
