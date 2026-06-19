<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
})

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      borderColor: '#3182f6',
      borderWidth: 2,
      tension: 0.3,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: '#3182f6',
      backgroundColor: (ctx) => {
        const { chart } = ctx
        const { ctx: c, chartArea } = chart
        if (!chartArea) return 'rgba(49,130,246,0.1)'
        const g = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
        g.addColorStop(0, 'rgba(49,130,246,0.35)')
        g.addColorStop(1, 'rgba(49,130,246,0)')
        return g
      },
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1c2230',
      borderColor: 'rgba(245,247,250,0.16)',
      borderWidth: 1,
      titleColor: '#9aa5b1',
      bodyColor: '#f5f7fa',
      padding: 10,
      callbacks: {
        label: (ctx) => `${Number(ctx.parsed.y).toLocaleString('ko-KR')}원`,
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6b7684', maxTicksLimit: 6 } },
    y: {
      grid: { color: 'rgba(245,247,250,0.06)' },
      ticks: { color: '#6b7684', callback: (v) => Number(v).toLocaleString('ko-KR') },
    },
  },
}
</script>

<template>
  <div class="chart-wrap">
    <Line :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.chart-wrap {
  height: 260px;
}
</style>
