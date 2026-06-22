<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const props = defineProps({
  labels: { type: Array, default: () => [] },
  closes: { type: Array, default: () => [] },
})

const option = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1c2230',
    borderColor: 'rgba(245,247,250,0.16)',
    borderWidth: 1,
    textStyle: { color: '#f5f7fa' },
    axisPointer: { type: 'line', label: { backgroundColor: '#2b3340' } },
    valueFormatter: (v) => Number(v).toLocaleString('ko-KR'),
  },
  grid: { left: 55, right: 20, bottom: 20, top: 16 },
  xAxis: {
    type: 'category',
    data: props.labels,
    axisLine: { lineStyle: { color: 'rgba(245,247,250,0.18)' } },
    axisLabel: { color: '#6b7684', fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    scale: true,
    axisLabel: { color: '#6b7684', formatter: (v) => Number(v).toLocaleString('ko-KR') },
    splitLine: { lineStyle: { color: 'rgba(245,247,250,0.06)' } },
  },
  series: [
    {
      name: '지수',
      type: 'line',
      data: props.closes,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#3182f6', width: 2 },
      itemStyle: { color: '#3182f6' },
      areaStyle: { color: 'rgba(49,130,246,0.10)' },
    },
  ],
}))
</script>

<template>
  <div class="chart-wrap">
    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart-wrap {
  height: 280px;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
