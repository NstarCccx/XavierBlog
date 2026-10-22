/** 中英文界面语言：localStorage 持久化，默认跟随浏览器。 */
import { ref, watch } from 'vue'

export type Locale = 'zh' | 'en'

const LOCALE_KEY = 'xb-locale'

function initial(): Locale {
  const saved = localStorage.getItem(LOCALE_KEY)
  if (saved === 'zh' || saved === 'en') return saved
  return (navigator.language || 'zh').toLowerCase().startsWith('zh') ? 'zh' : 'en'
}

const messages: Record<Locale, Record<string, string>> = {
  zh: {
    'nav.home': '首页',
    'nav.archive': '归档·分类',
    'nav.about': '关于',

    'hero.badge': '全栈 · 技术笔记 · 一直学习 · 一直构建',
    'hero.subtitle': '记录日常、开发代码与问题思考',
    'hero.start': '点击滚动阅读',
    'hero.about': 'About - Xavie Chan',
    'hero.scroll': '向下滑动探索',
    'hero.repo': '源码地址：',
    'hero.copy': '复制',
    'hero.copied': '已复制',
    'hero.copyFailed': '复制失败',

    'common.loading': '加载中…',
    'home.latest': '最新文章',
    'home.noPosts': '还没有文章',

    'post.views': '{n} 次阅读',
    'post.pinned': '置顶',

    'page.prev': '上一页',
    'page.next': '下一页',

    'archive.title': '归档·分类',
    'archive.total': '共 {n} 篇文章',
    'archive.count': '{n} 篇',
    'archive.all': '全部',
    'archive.empty': '该分类下暂无文章',

    'tax.title.category': '分类：{slug}',
    'tax.title.tag': '标签：{slug}',
    'tax.total': '共 {n} 篇文章',
    'tax.empty.category': '该分类下暂无文章',
    'tax.empty.tag': '该标签下暂无文章',

    'detail.toc': '目录',
    'detail.readTime': '约 {n} 分钟',
    'detail.end': '全文完',

    'about.title': 'About',
    'about.stack': '本站技术栈',
    'about.empty': '暂无内容',

    'comment.title': '评论（{n}）',
    'comment.nickname': '昵称 *',
    'comment.email': '邮箱（选填，仅博主可见）',
    'comment.content': '说点什么吧（提交后需审核）',
    'comment.submit': '发表评论',
    'comment.submitting': '提交中…',
    'comment.needNickname': '请输入昵称',
    'comment.needContent': '请输入评论内容',
    'comment.ok': '✓ 评论已提交，审核通过后会展示',
    'comment.reply': '回复',
    'comment.replyTo': '回复 {name}：',
    'comment.cancel': '取消',
    'comment.author': '博主',
    'comment.empty': '还没有评论，来抢沙发～',

    'nf.desc': '页面不存在或已被移除',
    'nf.back': '返回首页',
  },
  en: {
    'nav.home': 'Home',
    'nav.archive': 'Archive',
    'nav.about': 'About',

    'hero.badge': 'FULL-STACK · DEV NOTES · ALWAYS BUILDING',
    'hero.subtitle': 'Code, architecture and thoughts, written down.',
    'hero.start': 'Start Reading',
    'hero.about': 'About Me',
    'hero.scroll': 'SCROLL TO EXPLORE',
    'hero.repo': 'Project repository:',
    'hero.copy': 'Copy',
    'hero.copied': 'Copied',
    'hero.copyFailed': 'Copy failed',

    'common.loading': 'Loading…',
    'home.latest': 'Latest Posts',
    'home.noPosts': 'No posts yet',

    'post.views': '{n} views',
    'post.pinned': 'Pinned',

    'page.prev': 'Prev',
    'page.next': 'Next',

    'archive.title': 'Archive',
    'archive.total': '{n} posts in total',
    'archive.count': '{n} posts',
    'archive.all': 'All',
    'archive.empty': 'No posts in this category yet',

    'tax.title.category': 'Category: {slug}',
    'tax.title.tag': 'Tag: {slug}',
    'tax.total': '{n} posts',
    'tax.empty.category': 'No posts in this category yet',
    'tax.empty.tag': 'No posts with this tag yet',

    'detail.toc': 'Contents',
    'detail.readTime': '{n} min read',
    'detail.end': 'END',

    'about.title': 'About',
    'about.stack': 'Built With',
    'about.empty': 'Nothing here yet',

    'comment.title': 'Comments ({n})',
    'comment.nickname': 'Nickname *',
    'comment.email': 'Email (optional, visible only to me)',
    'comment.content': 'Say something… (comments are moderated)',
    'comment.submit': 'Post Comment',
    'comment.submitting': 'Posting…',
    'comment.needNickname': 'Nickname is required',
    'comment.needContent': 'Comment is required',
    'comment.ok': '✓ Submitted! It will appear after approval.',
    'comment.reply': 'Reply',
    'comment.replyTo': 'Replying to {name}:',
    'comment.cancel': 'Cancel',
    'comment.author': 'Author',
    'comment.empty': 'No comments yet — be the first!',

    'nf.desc': 'This page does not exist or has been removed.',
    'nf.back': 'Back to Home',
  },
}

const locale = ref<Locale>(initial())

watch(
  locale,
  (value) => {
    localStorage.setItem(LOCALE_KEY, value)
    document.documentElement.lang = value === 'zh' ? 'zh-CN' : 'en'
  },
  { immediate: true },
)

const MONTHS_EN = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

/** 归档分组用的年月标签，如「2026 年 5 月」/「May 2026」。 */
export function formatMonth(year: number, month: number): string {
  return locale.value === 'zh' ? `${year} 年 ${month} 月` : `${MONTHS_EN[month - 1]} ${year}`
}

export function useLocale() {
  function t(key: string, params?: Record<string, string | number>): string {
    let text = messages[locale.value][key] ?? messages.zh[key] ?? key
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        text = text.replaceAll(`{${k}}`, String(v))
      }
    }
    return text
  }

  function setLocale(value: Locale) {
    locale.value = value
  }

  return { locale, t, setLocale }
}
