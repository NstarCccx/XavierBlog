<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Document, ChatDotRound, Picture, Setting, PriceTag,
  Collection, DataBoard, SwitchButton, Fold, Expand, Monitor,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menus = [
  { index: '/', label: '仪表盘', icon: DataBoard },
  { index: '/posts', label: '文章管理', icon: Document },
  { index: '/categories', label: '分类管理', icon: Collection },
  { index: '/tags', label: '标签管理', icon: PriceTag },
  { index: '/comments', label: '评论管理', icon: ChatDotRound },
  { index: '/uploads', label: '图片库', icon: Picture },
  { index: '/settings', label: '站点设置', icon: Setting },
]

const collapsed = ref(false)
// 文章编辑页归属「文章管理」菜单
const activeMenu = computed(() => (route.path.startsWith('/posts') ? '/posts' : route.path))

const currentLabel = computed(() => {
  if (route.path === '/') return '仪表盘'
  if (route.path === '/posts/new') return '新建文章'
  if (/^\/posts\/\d+\/edit/.test(route.path)) return '编辑文章'
  return menus.find((m) => m.index === activeMenu.value)?.label ?? ''
})

onMounted(auth.loadMe)

function handleCommand(command: string) {
  if (command === 'logout') {
    auth.logout()
    router.push({ name: 'login' })
  }
}
</script>

<template>
  <el-container class="min-h-screen">
    <el-aside :width="collapsed ? '64px' : '216px'" class="admin-aside">
      <div class="flex h-14 items-center gap-2.5 overflow-hidden border-b border-white/10 px-4">
        <span
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 font-mono text-sm font-bold text-white shadow-lg shadow-indigo-500/30"
        >
          X
        </span>
        <span v-if="!collapsed" class="truncate text-sm font-bold text-white">XavierBlog·Console</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        :collapse="collapsed"
        :collapse-transition="false"
        class="admin-menu !border-r-0"
      >
        <el-menu-item v-for="menu in menus" :key="menu.index" :index="menu.index">
          <el-icon :size="17"><component :is="menu.icon" /></el-icon>
          <template #title>{{ menu.label }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-4">
        <div class="flex items-center gap-2">
          <el-button text class="!text-gray-500" @click="collapsed = !collapsed">
            <el-icon :size="18">
              <Fold v-if="!collapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>
              <span class="flex items-center gap-1">
                <el-icon :size="14"><Monitor /></el-icon>
                控制台
              </span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentLabel }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="flex items-center gap-4">
          <el-dropdown @command="handleCommand">
            <span class="flex cursor-pointer items-center gap-2">
              <span
                class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 text-sm font-bold text-white"
              >
                {{ (auth.nickname || auth.username || 'A')[0]!.toUpperCase() }}
              </span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="p-5">
        <router-view v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-aside {
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  transition: width 0.2s ease;
}

.admin-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: transparent;
  padding: 10px 8px;
}

.admin-aside :deep(.admin-menu .el-menu-item) {
  height: 44px;
  margin-bottom: 4px;
  border-radius: 10px;
  color: #94a3b8;
}

.admin-aside :deep(.admin-menu .el-menu-item:hover) {
  background: rgb(99 102 241 / 0.14);
  color: #fff;
}

.admin-aside :deep(.admin-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  box-shadow: 0 4px 12px rgb(99 102 241 / 0.35);
}
</style>
