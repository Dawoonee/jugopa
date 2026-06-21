<script setup>
import { computed } from 'vue'
import { useInView } from '@/composables/useInView'
import { formatSignedRate, changeClass } from '@/utils/format'

const props = defineProps({
  card: { type: Object, required: true }, // SectorCardNews + top_stocks
})

const { el, inView } = useInView()

// 게이지 정규화: top_stocks 중 |등락률| 최대를 100%로
const maxAbs = computed(() => {
  const rates = props.card.top_stocks.map((s) => Math.abs(Number(s.change_rate) || 0))
  return Math.max(...rates, 1)
})
function gaugeWidth(rate) {
  if (!inView.value) return '0%'
  return `${(Math.abs(Number(rate) || 0) / maxAbs.value) * 100}%`
}
</script>

<template>
  <article ref="el" class="sector card">
    <RouterLink :to="{ name: 'card-news-detail', params: { id: card.id } }" class="card-link">
      <header class="sector-head">
        <div>
          <span class="rank">#{{ card.rank }}</span>
          <h3 class="sector-name">{{ card.sector_name }}</h3>
        </div>
        <span class="count num">기사 {{ card.article_count }}건</span>
      </header>

      <p class="headline">{{ card.headline }}</p>
      <p class="summary">{{ card.summary }}</p>
      <span class="read-more">전문 보기 ›</span>
    </RouterLink>

    <div v-if="card.top_stocks?.length" class="gauges">
      <RouterLink
        v-for="s in card.top_stocks"
        :key="s.stock_code"
        :to="{ name: 'stock-detail', params: { code: s.stock_code } }"
        class="gauge-row"
      >
        <span class="g-name">{{ s.stock_name }}</span>
        <div class="g-track">
          <div
            class="g-fill"
            :class="changeClass(s.change_rate)"
            :style="{ width: gaugeWidth(s.change_rate) }"
          />
        </div>
        <span class="g-rate num" :class="changeClass(s.change_rate)">
          {{ formatSignedRate(s.change_rate) }}
        </span>
      </RouterLink>
    </div>
  </article>
</template>

<style scoped>
.sector {
  min-width: 320px;
  transition: transform var(--dur-base) var(--ease-out), border-color var(--dur-base);
}
.sector:hover {
  transform: translateY(-4px);
  border-color: var(--border-strong);
}
.card-link {
  display: block;
  color: inherit;
}
.read-more {
  display: inline-block;
  margin-bottom: var(--space-4);
  font-size: 12px;
  font-weight: 700;
  color: var(--accent);
}
.sector-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}
.rank {
  font-size: 12px;
  font-weight: 800;
  color: var(--accent);
}
.sector-name {
  font-size: 20px;
  font-weight: 800;
  margin-top: 2px;
}
.count {
  font-size: 12px;
  color: var(--text-tertiary);
}
.headline {
  font-weight: 700;
  line-height: 1.5;
  margin-bottom: 8px;
}
.summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.gauges {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid var(--border-subtle);
  padding-top: var(--space-4);
}
.gauge-row {
  display: grid;
  grid-template-columns: 88px 1fr 56px;
  align-items: center;
  gap: 10px;
  color: inherit;
  padding: 4px 6px;
  margin: 0 -6px;
  border-radius: var(--radius-sm);
  transition: background var(--dur-fast);
}
.gauge-row:hover {
  background: var(--bg-elevated);
}
.gauge-row:hover .g-name {
  color: var(--accent);
}
.g-name {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.g-track {
  height: 6px;
  background: var(--bg-base);
  border-radius: var(--radius-pill);
  overflow: hidden;
}
.g-fill {
  height: 100%;
  border-radius: var(--radius-pill);
  transition: width 0.8s var(--ease-out);
}
.g-fill.up {
  background: var(--up);
}
.g-fill.down {
  background: var(--down);
}
.g-fill.flat {
  background: var(--flat);
}
.g-rate {
  font-size: 12px;
  font-weight: 700;
  text-align: right;
}
@media (max-width: 767px) {
  .sector {
    min-width: 82vw;
  }
}
</style>
