import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'posts', name: 'post-list', component: () => import('@/views/post/PostList.vue') },
        { path: 'posts/new', name: 'post-new', component: () => import('@/views/post/PostEdit.vue') },
        { path: 'posts/:id/edit', name: 'post-edit', component: () => import('@/views/post/PostEdit.vue') },
        { path: 'categories', name: 'categories', component: () => import('@/views/CategoryManage.vue') },
        { path: 'tags', name: 'tags', component: () => import('@/views/TagManage.vue') },
        { path: 'comments', name: 'comments', component: () => import('@/views/CommentManage.vue') },
        { path: 'uploads', name: 'uploads', component: () => import('@/views/UploadManage.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

// 路由守卫：无 token 一律去登录页
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.token) {
    return { name: 'dashboard' }
  }
})

export default router
