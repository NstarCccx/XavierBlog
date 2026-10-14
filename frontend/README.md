# Frontend · 博客前台

Vue 3 + TypeScript + Vite + Tailwind CSS v4 + Pinia + Vue Router。

## 目录结构与职责

```
src/
├── api/            # 接口层：http.ts 是 axios 实例（统一错误处理），其余按模块拆分
├── components/
│   ├── layout/     # AppHeader（导航）、AppFooter
│   ├── post/       # PostCard（文章卡片）
│   ├── comment/    # CommentSection（评论表单+列表）、CommentItem（递归树）
│   └── common/     # Pagination（分页）
├── composables/    # 组合式函数：usePostList（列表页通用加载/分页逻辑）
├── router/         # 路由表
├── stores/         # Pinia：site（站点信息，启动加载一次）
├── types/          # TS 类型，与后端 app/schemas 一一对应
├── utils/          # markdown 渲染（高亮+目录提取）、日期格式化
├── views/          # 页面组件（每个路由一个）
│   ├── HomeView            # 首页：横幅 + 文章分页
│   ├── PostDetailView      # 详情：Markdown 渲染 + 侧边目录 + 评论
│   ├── TaxonomyListView    # 分类/标签文章列表（复用）
│   ├── ArchiveView         # 归档时间线
│   ├── AboutView           # 关于（读站点设置）
│   └── NotFoundView        # 404
├── App.vue         # 布局骨架：Header + router-view + Footer
├── main.ts         # 入口：注册 Pinia / Router
└── style.css       # Tailwind 入口 + Markdown 正文样式
```

## 开发

```bash
npm install
npm run dev      # http://localhost:5173（/api 代理到 8000 后端）
npm run build    # 类型检查 + 产物构建
```
