<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
} from 'chart.js'

ChartJS.register(BarElement, LinearScale, CategoryScale, Tooltip)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
})

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: 'rgba(138,149,161,0.5)',
      hoverBackgroundColor: '#3182f6',
      borderRadius: 3,
      maxBarThickness: 14,
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1c2230',
      borderColor: 'rgba(245,247,250,0.16)',
      borderWidth: 1,
      titleColor: '#9aa5b1',
      bodyColor: '#f5f7fa',
      callbacks: { label: (ctx) => `${Number(ctx.parsed.y).toLocaleString('ko-KR')}주` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6b7684', maxTicksLimit: 6 } },
    y: { grid: { color: 'rgba(245,247,250,0.06)' }, ticks: { color: '#6b7684', maxTicksLimit: 4 } },
  },
}
</script>

<template>
  <div class="vol-wrap">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<style scoped>
.vol-wrap {
  height: 130px;
}
</style>
