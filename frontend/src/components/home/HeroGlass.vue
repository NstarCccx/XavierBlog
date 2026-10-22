<script setup lang="ts">
/**
 * 首页琉璃 Hero：
 * - Canvas 绘制流动的彩色光斑（琉璃质感）+ 科技网格 + 粒子 + 点击涟漪
 * - 站点名拆成字母，渲染成磨砂玻璃块，鼠标视差 + 悬浮动画
 * - 鼠标光晕跟随、HUD 四角装饰与坐标读数
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useSiteStore } from '@/stores/site'
import { useLocale } from '@/composables/useLocale'
import { useTheme } from '@/composables/useTheme'

const site = useSiteStore()
const { t } = useLocale()
const { theme } = useTheme()

const sectionEl = ref<HTMLElement | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)

/** 项目仓库地址 */
const REPO_URL = 'https://github.com/NstarCccx/XavierBlog'

/** 复制状态：copied 短暂展示成功提示，failed 展示失败提示 */
type CopyState = 'idle' | 'copied' | 'failed'
const copyState = ref<CopyState>('idle')
let copyTimer: number | undefined

async function copyRepoUrl() {
  const ok = await writeClipboard(REPO_URL)
  copyState.value = ok ? 'copied' : 'failed'
  window.clearTimeout(copyTimer)
  copyTimer = window.setTimeout(() => {
    copyState.value = 'idle'
  }, 2000)
}

/** 优先用 Clipboard API，非安全上下文（如 http 部署）回退到 execCommand */
async function writeClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {
      // 继续尝试回退方案
    }
  }
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.setAttribute('readonly', '')
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    return ok
  } catch {
    return false
  }
}

const letters = computed(() => Array.from((site.info.site_name || 'XavierBlog').trim().slice(0, 12)))

/** 归一化指针位置（0~1），供 DOM 视差、光晕与 HUD 读数使用 */
const pointer = ref({ x: 0.5, y: 0.5, inside: false })

/* ---------------- Canvas：流动琉璃 ---------------- */

interface Blob {
  bx: number; by: number; r: number      // 基准位置与半径（相对）
  ax: number; ay: number                 // 漂移幅度
  fx: number; fy: number; ph: number     // 漂移频率与相位
  depth: number                          // 鼠标跟随强度
  color: number                          // 调色板索引
}

const BLOBS: Blob[] = [
  { bx: 0.16, by: 0.30, r: 0.34, ax: 0.07, ay: 0.10, fx: 0.23, fy: 0.17, ph: 0.0, depth: 0.9, color: 0 },
  { bx: 0.84, by: 0.24, r: 0.30, ax: 0.06, ay: 0.09, fx: 0.19, fy: 0.24, ph: 1.3, depth: 1.2, color: 2 },
  { bx: 0.62, by: 0.72, r: 0.36, ax: 0.08, ay: 0.07, fx: 0.16, fy: 0.21, ph: 2.6, depth: 0.7, color: 1 },
  { bx: 0.30, by: 0.82, r: 0.28, ax: 0.05, ay: 0.08, fx: 0.27, fy: 0.15, ph: 4.1, depth: 1.4, color: 3 },
  { bx: 0.48, by: 0.44, r: 0.30, ax: 0.06, ay: 0.06, fx: 0.13, fy: 0.19, ph: 5.2, depth: 0.5, color: 4 },
  { bx: 0.94, by: 0.82, r: 0.24, ax: 0.05, ay: 0.07, fx: 0.22, fy: 0.13, ph: 0.8, depth: 1.1, color: 5 },
]

const PALETTE_LIGHT = ['99,102,241', '139,92,246', '6,182,212', '236,72,153', '59,130,246', '168,85,247']
const PALETTE_DARK = ['99,102,241', '139,92,246', '34,211,238', '244,114,182', '96,165,250', '192,132,252']

interface Particle { x: number; y: number; r: number; vx: number; vy: number; tw: number; plus: boolean }
interface Ripple { x: number; y: number; r: number; alpha: number }
interface CodeDrop { x: number; y: number; speed: number; chars: string[]; alpha: number }

const particles: Particle[] = []
const ripples: Ripple[] = []
const codeDrops: CodeDrop[] = []

// 代码流字符集
const CODE_CHARS = 'const let var function return if else for while import export from async await => {} [] () = + - * / < > & | ! @ # $ % ^ ~ _ 0123456789abcdef'.split('')

let ctx: CanvasRenderingContext2D | null = null
let resizeObserver: ResizeObserver | null = null
let rafId = 0
let w = 0
let h = 0
let time = 0
let lastTs = 0
const reducedMotion =
  typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

// 鼠标目标与当前值（当前值逐帧插值，让光斑有惯性感）
const mouse = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, inside: false }

function initParticles() {
  particles.length = 0
  const count = Math.min(48, Math.round((w * h) / 22000))
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      r: 0.8 + Math.random() * 1.4,
      vx: (Math.random() - 0.5) * 10,
      vy: (Math.random() - 0.5) * 10,
      tw: Math.random() * Math.PI * 2,
      plus: Math.random() < 0.25,
    })
  }
}

function initCodeDrops() {
  codeDrops.length = 0
  const count = Math.min(24, Math.round(w / 60))
  for (let i = 0; i < count; i++) {
    codeDrops.push({
      x: Math.random() * w,
      y: Math.random() * h - h,
      speed: 30 + Math.random() * 50,
      chars: Array.from({ length: 8 + Math.floor(Math.random() * 6) }, () =>
        CODE_CHARS[Math.floor(Math.random() * CODE_CHARS.length)]!
      ),
      alpha: 0.15 + Math.random() * 0.25,
    })
  }
}

function resize() {
  const canvas = canvasEl.value
  if (!canvas || !ctx) return
  const rect = canvas.getBoundingClientRect()
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  w = Math.max(1, rect.width)
  h = Math.max(1, rect.height)
  canvas.width = Math.round(w * dpr)
  canvas.height = Math.round(h * dpr)
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  initParticles()
  initCodeDrops()
}

function drawGrid(dark: boolean) {
  if (!ctx) return
  ctx.strokeStyle = dark ? 'rgba(148,163,184,0.06)' : 'rgba(79,70,229,0.065)'
  ctx.lineWidth = 1
  ctx.beginPath()
  for (let x = 0.5; x < w; x += 48) {
    ctx.moveTo(x, 0)
    ctx.lineTo(x, h)
  }
  for (let y = 0.5; y < h; y += 48) {
    ctx.moveTo(0, y)
    ctx.lineTo(w, y)
  }
  ctx.stroke()
}

function drawBlobs(dark: boolean) {
  if (!ctx) return
  const palette = dark ? PALETTE_DARK : PALETTE_LIGHT
  const maxDim = Math.max(w, h)
  const dx = mouse.inside ? (mouse.x - 0.5) * 2 : 0
  const dy = mouse.inside ? (mouse.y - 0.5) * 2 : 0
  ctx.globalCompositeOperation = dark ? 'lighter' : 'source-over'
  for (const b of BLOBS) {
    const cx = (b.bx + Math.sin(time * b.fx + b.ph) * b.ax) * w + dx * w * 0.05 * b.depth
    const cy = (b.by + Math.cos(time * b.fy + b.ph) * b.ay) * h + dy * h * 0.09 * b.depth
    const r = b.r * maxDim * 0.6
    const c = palette[b.color]!
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    g.addColorStop(0, `rgba(${c},${dark ? 0.34 : 0.42})`)
    g.addColorStop(0.55, `rgba(${c},${dark ? 0.12 : 0.16})`)
    g.addColorStop(1, `rgba(${c},0)`)
    ctx.fillStyle = g
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.globalCompositeOperation = 'source-over'
}

function drawGlare(dark: boolean) {
  if (!ctx || !mouse.inside) return
  const gx = mouse.x * w
  const gy = mouse.y * h
  const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, 300)
  g.addColorStop(0, dark ? 'rgba(255,255,255,0.10)' : 'rgba(255,255,255,0.30)')
  g.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.globalCompositeOperation = dark ? 'screen' : 'source-over'
  ctx.fillStyle = g
  ctx.fillRect(gx - 300, gy - 300, 600, 600)
  ctx.globalCompositeOperation = 'source-over'
}

function drawCodeStream(dark: boolean, dt: number) {
  if (!ctx) return
  const fontSize = 13
  ctx.font = `${fontSize}px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`
  ctx.textBaseline = 'top'

  for (const drop of codeDrops) {
    if (!reducedMotion) {
      drop.y += drop.speed * dt
      // 随机替换字符
      if (Math.random() < 0.03) {
        const idx = Math.floor(Math.random() * drop.chars.length)
        drop.chars[idx] = CODE_CHARS[Math.floor(Math.random() * CODE_CHARS.length)]!
      }
      // 重置到顶部
      if (drop.y > h + 100) {
        drop.y = -drop.chars.length * fontSize - Math.random() * 200
        drop.x = Math.random() * w
      }
    }

    // 绘制模糊的代码字符
    for (let i = 0; i < drop.chars.length; i++) {
      const charY = drop.y + i * fontSize
      if (charY < -fontSize || charY > h + fontSize) continue

      // 越往下越淡
      const fadeRatio = 1 - (i / drop.chars.length) * 0.7
      const alpha = drop.alpha * fadeRatio

      // 模糊效果：使用阴影
      ctx.shadowBlur = 8
      ctx.shadowColor = dark ? `rgba(100, 180, 255, ${alpha * 0.5})` : `rgba(99, 102, 241, ${alpha * 0.5})`
      ctx.fillStyle = dark ? `rgba(140, 200, 255, ${alpha})` : `rgba(99, 102, 241, ${alpha})`
      ctx.fillText(drop.chars[i]!, drop.x, charY)
    }
  }
  ctx.shadowBlur = 0
}

function drawParticles(dark: boolean, dt: number) {
  if (!ctx) return
  for (const p of particles) {
    if (!reducedMotion) {
      p.x += p.vx * dt
      p.y += p.vy * dt
      if (p.x < -10) p.x = w + 10
      if (p.x > w + 10) p.x = -10
      if (p.y < -10) p.y = h + 10
      if (p.y > h + 10) p.y = -10
    }
    const a = (0.18 + 0.22 * (0.5 + 0.5 * Math.sin(time * 1.6 + p.tw))) * (dark ? 0.9 : 0.8)
    ctx.fillStyle = dark ? `rgba(165,180,252,${a})` : `rgba(99,102,241,${a})`
    ctx.strokeStyle = ctx.fillStyle
    ctx.lineWidth = 1
    if (p.plus) {
      ctx.beginPath()
      ctx.moveTo(p.x - 3 * p.r, p.y)
      ctx.lineTo(p.x + 3 * p.r, p.y)
      ctx.moveTo(p.x, p.y - 3 * p.r)
      ctx.lineTo(p.x, p.y + 3 * p.r)
      ctx.stroke()
    } else {
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fill()
    }
  }
}

function drawRipples(dark: boolean, dt: number) {
  if (!ctx) return
  const c = dark ? '165,180,252' : '99,102,241'
  for (let i = ripples.length - 1; i >= 0; i--) {
    const rp = ripples[i]!
    if (!reducedMotion) {
      rp.r += 320 * dt
      rp.alpha -= dt * 0.9
    }
    if (rp.alpha <= 0) {
      ripples.splice(i, 1)
      continue
    }
    ctx.lineWidth = 1.5
    ctx.strokeStyle = `rgba(${c},${(rp.alpha * 0.5).toFixed(3)})`
    ctx.beginPath()
    ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2)
    ctx.stroke()
    ctx.strokeStyle = `rgba(${c},${(rp.alpha * 0.25).toFixed(3)})`
    ctx.beginPath()
    ctx.arc(rp.x, rp.y, rp.r * 0.7, 0, Math.PI * 2)
    ctx.stroke()
  }
}

function draw(dt: number) {
  if (!ctx) return
  const dark = theme.value === 'dark'
  if (!reducedMotion) {
    time += dt
    mouse.x += (mouse.tx - mouse.x) * 0.07
    mouse.y += (mouse.ty - mouse.y) * 0.07
  }
  ctx.clearRect(0, 0, w, h)
  drawBlobs(dark)
  drawGrid(dark)
  drawCodeStream(dark, dt)
  drawGlare(dark)
  drawParticles(dark, dt)
  drawRipples(dark, dt)
}

function loop(ts: number) {
  rafId = requestAnimationFrame(loop)
  const dt = Math.min(Math.max((ts - lastTs) / 1000, 0), 0.05)
  lastTs = ts
  draw(dt)
}

/* ---------------- 指针交互 ---------------- */

function onPointerMove(e: PointerEvent) {
  const rect = sectionEl.value?.getBoundingClientRect()
  if (!rect || rect.width === 0 || rect.height === 0) return
  pointer.value = {
    x: Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1),
    y: Math.min(Math.max((e.clientY - rect.top) / rect.height, 0), 1),
    inside: true,
  }
  mouse.tx = pointer.value.x
  mouse.ty = pointer.value.y
  mouse.inside = true
}

function onPointerLeave() {
  pointer.value = { ...pointer.value, inside: false }
  mouse.inside = false
}

function onPointerDown(e: PointerEvent) {
  if (reducedMotion || ripples.length > 6) return
  const rect = sectionEl.value?.getBoundingClientRect()
  if (!rect) return
  ripples.push({
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
    r: 6,
    alpha: 1,
  })
}

/* ---------------- DOM 视差样式 ---------------- */

function letterStyle(i: number) {
  const n = Math.max(letters.value.length, 1)
  const d = 0.35 + (i / n) * 0.85
  const nx = pointer.value.inside ? pointer.value.x * 2 - 1 : 0
  const ny = pointer.value.inside ? pointer.value.y * 2 - 1 : 0
  return {
    transform: `translate3d(${(-nx * 24 * d).toFixed(2)}px, ${(-ny * 16 * d).toFixed(2)}px, 0)`,
    transition: pointer.value.inside
      ? 'transform 0.25s cubic-bezier(0.22, 1, 0.36, 1)'
      : 'transform 0.8s cubic-bezier(0.22, 1, 0.36, 1)',
  }
}

function floatStyle(i: number) {
  return {
    animationDelay: `${(i % 6) * 0.45}s`,
    animationDuration: `${5 + (i % 4) * 0.7}s`,
  }
}

const glareStyle = computed(() => {
  if (!pointer.value.inside) return { opacity: '0' }
  const x = (pointer.value.x * 100).toFixed(1)
  const y = (pointer.value.y * 100).toFixed(1)
  return {
    opacity: '1',
    background: `radial-gradient(360px circle at ${x}% ${y}%, rgba(255,255,255,${theme.value === 'dark' ? 0.1 : 0.32}), transparent 65%)`,
  }
})

watch(theme, () => {
  if (reducedMotion) draw(0)
})

onMounted(() => {
  const canvas = canvasEl.value
  ctx = canvas?.getContext('2d') ?? null
  resize()
  resizeObserver = new ResizeObserver(() => {
    resize()
    if (reducedMotion) draw(0)
  })
  if (canvas) resizeObserver.observe(canvas)
  if (reducedMotion) {
    draw(0)
  } else {
    rafId = requestAnimationFrame(loop)
  }
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  resizeObserver?.disconnect()
  window.clearTimeout(copyTimer)
})
</script>

<template>
  <section
    ref="sectionEl"
    class="full-bleed relative isolate flex h-[calc(100vh-4rem)] min-h-[480px] flex-col overflow-hidden select-none supports-[height:100svh]:h-[calc(100svh-4rem)]"
    @pointermove="onPointerMove"
    @pointerleave="onPointerLeave"
    @pointerdown="onPointerDown"
  >
    <!-- 主题底色 -->
    <div
      class="absolute inset-0 bg-gradient-to-b from-indigo-50 via-violet-50 to-stone-50 dark:from-[#0a0c14] dark:via-[#101528] dark:to-[#0a0c12]"
      aria-hidden="true"
    />
    <canvas ref="canvasEl" class="absolute inset-0 h-full w-full" aria-hidden="true" />

    <!-- 鼠标光晕 -->
    <div
      class="pointer-events-none absolute inset-0 hidden transition-opacity duration-500 md:block"
      :style="glareStyle"
      aria-hidden="true"
    />

    <!-- HUD 四角 -->
    <span class="pointer-events-none absolute top-5 left-5 h-6 w-6 border-t-2 border-l-2 border-indigo-400/50 dark:border-indigo-400/30" aria-hidden="true" />
    <span class="pointer-events-none absolute top-5 right-5 h-6 w-6 border-t-2 border-r-2 border-indigo-400/50 dark:border-indigo-400/30" aria-hidden="true" />
    <span class="pointer-events-none absolute bottom-5 left-5 h-6 w-6 border-b-2 border-l-2 border-indigo-400/50 dark:border-indigo-400/30" aria-hidden="true" />
    <span class="pointer-events-none absolute right-5 bottom-5 h-6 w-6 border-r-2 border-b-2 border-indigo-400/50 dark:border-indigo-400/30" aria-hidden="true" />

    <!-- 主内容 -->
    <div class="relative z-10 flex flex-1 flex-col items-center justify-center px-6 text-center">
      <p class="mb-3 font-mono text-[11px] tracking-[0.35em] text-indigo-500/80 uppercase sm:text-xs dark:text-cyan-300/80">
        {{ t('hero.badge') }}
      </p>

      <!-- 项目仓库地址：点击右侧按钮复制 -->
      <div class="mb-8 flex flex-wrap items-center justify-center gap-2 text-xs">
        <span class="text-stone-500 dark:text-stone-400">{{ t('hero.repo') }}</span>
        <code
          class="select-text rounded-md border border-stone-900/10 bg-white/50 px-2 py-1 font-mono text-[11px] text-stone-600 sm:text-xs dark:border-white/15 dark:bg-white/5 dark:text-stone-300"
        >
          {{ REPO_URL }}
        </code>
        <button
          type="button"
          class="inline-flex items-center gap-1 rounded-md border border-stone-900/10 bg-white/50 px-2 py-1 font-mono text-[11px] text-stone-500 transition-colors hover:border-indigo-300 hover:text-indigo-600 sm:text-xs dark:border-white/15 dark:bg-white/5 dark:text-stone-400 dark:hover:border-amber-300/50 dark:hover:text-amber-300"
          :aria-label="t('hero.copy')"
          @click.stop="copyRepoUrl"
        >
          <svg
            v-if="copyState === 'idle'"
            class="h-3.5 w-3.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          <svg
            v-else-if="copyState === 'copied'"
            class="h-3.5 w-3.5 text-emerald-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <svg
            v-else
            class="h-3.5 w-3.5 text-rose-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M15 9l-6 6M9 9l6 6" />
          </svg>
          <span
            :class="copyState === 'copied' ? 'text-emerald-500' : copyState === 'failed' ? 'text-rose-500' : ''"
          >
            {{ copyState === 'copied' ? t('hero.copied') : copyState === 'failed' ? t('hero.copyFailed') : t('hero.copy') }}
          </span>
        </button>
      </div>

      <div class="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
        <div v-for="(ch, i) in letters" :key="i" :style="letterStyle(i)">
          <span class="hero-glass hero-float text-3xl sm:text-4xl md:text-5xl" :style="floatStyle(i)">
            {{ ch }}
          </span>
        </div>
      </div>

      <p class="mt-8 max-w-xl text-sm text-stone-500 sm:text-base dark:text-stone-400">
        {{ site.info.site_description || t('hero.subtitle') }}
      </p>

      <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
        <a href="#posts" class="btn-primary">
          {{ t('hero.start') }}
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14m0 0l-6-6m6 6l6-6" />
          </svg>
        </a>
        <router-link :to="{ name: 'about' }" class="btn-glass">
          {{ t('hero.about') }}
        </router-link>
      </div>
    </div>

    <!-- HUD 坐标读数 -->
    <p
      class="pointer-events-none absolute right-7 bottom-7 hidden font-mono text-[10px] tracking-widest text-stone-400/80 md:block dark:text-stone-500"
    >
      X {{ pointer.x.toFixed(2) }} · Y {{ pointer.y.toFixed(2) }} · {{ theme === 'dark' ? 'DARK' : 'LIGHT' }}
    </p>

    <!-- 滚动提示（置于渐隐层之后，避免被底部不透明渐变盖住） -->
    <div class="pointer-events-none absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center gap-2">
      <span class="font-mono text-sm tracking-[0.3em] text-stone-400 uppercase sm:text-base sm:tracking-[0.35em] dark:text-stone-300">
        {{ t('hero.scroll') }}
      </span>
      <svg
        class="hero-bounce h-5 w-5 text-indigo-400 sm:h-6 sm:w-6 dark:text-cyan-300"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M6 9l6 6 6-6" />
      </svg>
    </div>

    <!-- 底部渐隐，融入正文 -->
    <div class="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-b from-transparent to-stone-50 dark:to-[#0a0c12]" aria-hidden="true" />
  </section>
</template>
