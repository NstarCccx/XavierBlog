/** Markdown 渲染：代码高亮 + 标题目录提取。 */
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import type { Token } from 'markdown-it'

export interface TocItem {
  id: string
  text: string
  level: number
}

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

/** 给标题 token 注入 id，并收集目录。 */
export function renderMarkdown(content: string): { html: string; toc: TocItem[] } {
  const toc: TocItem[] = []
  let headingIndex = 0

  md.renderer.rules.heading_open = (tokens: Token[], idx: number) => {
    const token = tokens[idx]
    const textToken = tokens[idx + 1]
    const text = textToken?.content ?? ''
    const id = `heading-${headingIndex++}`
    toc.push({ id, text, level: Number(token.tag.slice(1)) })
    return `<${token.tag} id="${id}" class="heading-anchor">`
  }

  const html = md.render(content)
  delete md.renderer.rules.heading_open // 还原，避免污染后续渲染
  return { html, toc: toc.filter((t) => t.level >= 2 && t.level <= 3) }
}
