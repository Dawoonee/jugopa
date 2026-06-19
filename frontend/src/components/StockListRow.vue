<script setup>
import { formatNumber, formatSignedRate, changeClass } from '@/utils/format'

defineProps({
  stock: { type: Object, required: true }, // { stock_code, stock_name, close_price, change_rate }
})
</script>

<template>
  <RouterLink :to="{ name: 'stock-detail', params: { code: stock.stock_code } }" class="row">
    <div class="row-info">
      <span class="row-name">{{ stock.stock_name }}</span>
      <span class="row-code num">{{ stock.stock_code }}</span>
    </div>
    <div class="row-price">
      <span class="row-close num">{{ formatNumber(stock.close_price) }}</span>
      <span class="row-rate num" :class="changeClass(stock.change_rate)">
        {{ formatSignedRate(stock.change_rate) }}
      </span>
    </div>
  </RouterLink>
</template>

<style scoped>
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px var(--space-4);
  border-radius: var(--radius-md);
  transition: background var(--dur-fast);
}
.row:hover {
  background: var(--bg-hover);
}
.row-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.row-name {
  font-weight: 700;
}
.row-code {
  font-size: 12px;
  color: var(--text-tertiary);
}
.row-price {
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.row-close {
  font-weight: 700;
}
.row-rate {
  font-size: 13px;
  font-weight: 600;
}
</style>
