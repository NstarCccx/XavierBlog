# Admin · 管理后台

Vue 3 + TypeScript + Vite + Element Plus + Pinia + md-editor-v3。

## 目录结构与职责

```
src/
├── api/
│   ├── http.ts     # axios 实例：自动带 Bearer token、401 统一跳登录、错误提示
│   └── index.ts    # 全部后端接口封装（auth/posts/categories/tags/comments/uploads/设置）
├── layouts/
│   └── AdminLayout.vue   # 侧边栏 + 顶栏布局，所有管理页共用
├── router/         # 路由 + 全局守卫（无 token 跳 /login）
├── stores/
│   └── auth.ts     # 登录态：token 持久化 localStorage、当前用户信息
├── types/          # TS 类型，与后端 app/schemas 一一对应
├── views/
│   ├── LoginView.vue       # 登录页
│   ├── DashboardView.vue   # 仪表盘统计
│   ├── post/PostList.vue   # 文章列表（搜索/筛选/分页/删除）
│   ├── post/PostEdit.vue   # 新建/编辑（md-editor-v3、分类标签、图片上传）
│   ├── CategoryManage.vue  # 分类 CRUD
│   ├── TagManage.vue       # 标签 CRUD
│   ├── CommentManage.vue   # 评论审核/回复/删除
│   ├── UploadManage.vue    # 图片库
│   └── SettingsView.vue    # 站点设置 + 修改密码
├── App.vue         # 根组件（路由出口）
├── main.ts         # 入口：Pinia / Router / Element Plus（中文语言包）
└── style.css       # 全局补充样式
```

## 开发

```bash
npm install
npm run dev      # http://localhost:5174（/api 代理到 8000 后端）
npm run build    # 类型检查 + 产物构建
```

默认账号：`admin / admin123`（登录后可在「站点设置 → 修改密码」修改）
