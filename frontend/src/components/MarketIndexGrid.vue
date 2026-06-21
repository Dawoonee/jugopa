<script setup>
import { formatNumber, formatSignedRate, formatSignedNumber, changeClass } from '@/utils/format'

defineProps({
  indices: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="grid">
    <div v-for="idx in indices" :key="idx.index_name" class="cell">
      <span class="cell-name">{{ idx.index_name }}</span>
      <span class="cell-price num">{{ formatNumber(idx.close_price, 2) }}</span>
      <span class="cell-change num" :class="changeClass(idx.change_rate)">
        {{ formatSignedNumber(idx.change, 2) }} ({{ formatSignedRate(idx.change_rate) }})
      </span>
    </div>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}
.cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--space-4);
  background: var(--glass-bg, rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.3));
  border-radius: var(--radius-md);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}
.cell-name {
  font-size: 13px;
  color: inherit;
  opacity: 0.85;
  font-weight: 600;
}
.cell-price {
  font-size: 20px;
  font-weight: 800;
}
.cell-change {
  font-size: 12px;
  font-weight: 600;
}
@media (max-width: 767px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
