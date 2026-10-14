<script setup lang="ts">
/** 文章浏览量横向柱状图（echarts/core 按需引入，随仪表盘异步加载）。 */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ComposeOption } from 'echarts/core'
import type { BarSeriesOption } from 'echarts/charts'
import type { GridComponentOption, TooltipComponentOption } from 'echarts/components'
import type { PostViewsItem } from '@/types'

echarts.use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

type Option = ComposeOption<BarSeriesOption | GridComponentOption | TooltipComponentOption>

const props = defineProps<{ items: PostViewsItem[] }>()

const el = ref<HTMLDivElement | null>(null)
let chart: ReturnType<typeof echarts.init> | null = null
let observer: ResizeObserver | null = null

function render() {
  if (!chart) return
  const list = [...props.items].reverse()
  const option: Option = {
    grid: { left: 8, right: 32, top: 6, bottom: 6, outerBoundsMode: 'same', outerBoundsContain: 'axisLabel' },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      formatter: '{b}<br/>浏览量：{c}',
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef2f7' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
    },
    yAxis: {
      type: 'category',
      data: list.map((i) => i.title),
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { color: '#475569', fontSize: 12, width: 150, overflow: 'truncate' },
    },
    series: [
      {
        name: '浏览量',
        type: 'bar',
        data: list.map((i) => i.views),
        barMaxWidth: 16,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#818cf8' },
              { offset: 1, color: '#6366f1' },
            ],
          },
        },
      },
    ],
  }
  chart.setOption(option)
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value)
  render()
  observer = new ResizeObserver(() => chart?.resize())
  observer.observe(el.value)
})

watch(() => props.items, render)

onBeforeUnmount(() => {
  observer?.disconnect()
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="el" class="h-72 w-full" />
</template>
