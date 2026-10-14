/** 明暗主题：localStorage 持久化，默认跟随系统。 */
import { ref, watch } from 'vue'

export type Theme = 'light' | 'dark'

const THEME_KEY = 'xb-theme'

function initial(): Theme {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// 模块级单例：所有组件共享同一份主题状态
const theme = ref<Theme>(initial())

watch(
  theme,
  (value) => {
    document.documentElement.classList.toggle('dark', value === 'dark')
    localStorage.setItem(THEME_KEY, value)
  },
  { immediate: true },
)

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  return { theme, toggle }
}
