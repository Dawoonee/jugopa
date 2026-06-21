<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  labels: { type: Array, default: () => [] },
  closes: { type: Array, default: () => [] },
  volumes: { type: Array, default: () => [] },
})

const option = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1c2230',
    borderColor: 'rgba(245,247,250,0.16)',
    borderWidth: 1,
    textStyle: { color: '#f5f7fa' },
    axisPointer: { type: 'cross', label: { backgroundColor: '#2b3340' } },
    valueFormatter: (v) => Number(v).toLocaleString('ko-KR'),
  },
  legend: {
    data: ['종가', '거래량'],
    textStyle: { color: '#9aa5b1' },
    top: 0,
  },
  grid: { left: 45, right: 45, bottom: 20, top: 36 },
  xAxis: {
    type: 'category',
    data: props.labels,
    axisLine: { lineStyle: { color: 'rgba(245,247,250,0.18)' } },
    axisLabel: { color: '#6b7684', fontSize: 11 },
  },
  yAxis: [
    {
      type: 'value',
      name: '종가',
      position: 'left',
      scale: true,
      nameTextStyle: { color: '#6b7684' },
      axisLabel: { color: '#6b7684', formatter: (v) => Number(v).toLocaleString('ko-KR') },
      splitLine: { lineStyle: { color: 'rgba(245,247,250,0.06)' } },
    },
    {
      type: 'value',
      name: '거래량',
      position: 'right',
      nameTextStyle: { color: '#6b7684' },
      axisLabel: {
        color: '#6b7684',
        formatter: (v) => (v >= 10000 ? `${(v / 10000).toFixed(0)}만` : v),
      },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: '거래량',
      type: 'bar',
      yAxisIndex: 1,
      data: props.volumes,
      itemStyle: { color: 'rgba(122,138,160,0.45)' },
      barWidth: '55%',
    },
    {
      name: '종가',
      type: 'line',
      yAxisIndex: 0,
      data: props.closes,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#3182f6', width: 2 },
      itemStyle: { color: '#3182f6' },
    },
  ],
}))
</script>

<template>
  <div class="combo-wrap">
    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<style scoped>
.combo-wrap {
  height: 280px;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
