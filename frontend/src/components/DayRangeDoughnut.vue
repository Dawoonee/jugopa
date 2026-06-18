<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js'
import { formatNumber } from '@/utils/format'

ChartJS.register(DoughnutController, ArcElement, Tooltip, Legend)

const props = defineProps({
  high: { type: Number, default: 0 },
  low: { type: Number, default: 0 },
  close: { type: Number, default: 0 },
})

// 당일 변동 폭(저가→고가)을 종가 기준으로 두 구간으로 나눠 표시
const lowToClose = computed(() => Math.max(props.close - props.low, 0))
const closeToHigh = computed(() => Math.max(props.high - props.close, 0))
const flat = computed(() => lowToClose.value === 0 && closeToHigh.value === 0)

const chartData = computed(() => ({
  labels: ['저가 → 종가', '종가 → 고가'],
  datasets: [
    {
      data: flat.value ? [1, 0] : [lowToClose.value, closeToHigh.value],
      backgroundColor: ['#3182f6', 'rgba(245,247,250,0.12)'],
      borderColor: '#1c2230',
      borderWidth: 2,
      hoverOffset: 4,
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#9aa5b1', boxWidth: 10, padding: 12, font: { size: 11 } },
    },
    tooltip: {
      backgroundColor: '#1c2230',
      borderColor: 'rgba(245,247,250,0.16)',
      borderWidth: 1,
      titleColor: '#9aa5b1',
      bodyColor: '#f5f7fa',
      padding: 10,
      callbacks: {
        label: (ctx) => `${ctx.label}: ${formatNumber(ctx.parsed)}원`,
      },
    },
  },
}
</script>

<template>
  <div class="doughnut-wrap">
    <div class="chart-area">
      <Doughnut :data="chartData" :options="options" />
      <div class="center">
        <span class="center-label">종가</span>
        <span class="center-value num">{{ formatNumber(close) }}</span>
      </div>
    </div>
    <div class="range">
      <span class="range-item"><i class="dot low" /> 저가 {{ formatNumber(low) }}</span>
      <span class="range-item"><i class="dot high" /> 고가 {{ formatNumber(high) }}</span>
    </div>
  </div>
</template>

<style scoped>
.doughnut-wrap {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.chart-area {
  position: relative;
  height: 200px;
}
.center {
  position: absolute;
  top: 42%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  pointer-events: none;
}
.center-label {
  font-size: 12px;
  color: var(--text-tertiary);
}
.center-value {
  font-size: 20px;
  font-weight: 800;
}
.range {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  font-size: 12px;
  color: var(--text-secondary);
}
.range-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.low {
  background: #3182f6;
}
.dot.high {
  background: rgba(245, 247, 250, 0.4);
}
</style>
