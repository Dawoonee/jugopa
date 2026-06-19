<script setup>
import { ref, onMounted } from 'vue'
import { stocksApi } from '@/api/stocks'
import { formatDate } from '@/utils/format'
import MarketIndexGrid from '@/components/MarketIndexGrid.vue'
import MarketMoodBanner from '@/components/MarketMoodBanner.vue'
import Skeleton from '@/components/common/Skeleton.vue'

const indices = ref([])
const weather = ref(null)
const loading = ref(true)
const today = formatDate()

onMounted(async () => {
  try {
    const [idxRes, weatherRes] = await Promise.allSettled([
      stocksApi.indices(),
      stocksApi.weatherToday(),
    ])
    if (idxRes.status === 'fulfilled') indices.value = idxRes.value.data
    if (weatherRes.status === 'fulfilled') weather.value = weatherRes.value.data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page home">
    <header class="home-head">
      <RouterLink :to="{ name: 'knowledge' }" class="nav-arrow" aria-label="경제 지식">‹</RouterLink>
      <p class="home-date">{{ today }}</p>
      <RouterLink :to="{ name: 'recommend' }" class="nav-arrow" aria-label="주식 추천">›</RouterLink>
    </header>

    <section class="home-mood">
      <Skeleton v-if="loading" height="140px" radius="var(--radius-xl)" />
      <MarketMoodBanner v-else :weather="weather" />
    </section>

    <section class="home-indices">
      <h2 class="section-title">오늘의 시장 지표</h2>
      <div v-if="loading" class="idx-skeleton">
        <Skeleton v-for="n in 4" :key="n" height="84px" radius="var(--radius-md)" />
      </div>
      <MarketIndexGrid v-else :indices="indices" />
    </section>

    <RouterLink :to="{ name: 'mypage' }" class="scroll-hint">
      마이페이지 보기 <span class="chev">⌄</span>
    </RouterLink>
  </div>
</template>

<style scoped>
.home-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}
.home-date {
  font-size: 16px;
  font-weight: 700;
}
.nav-arrow {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-pill);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 20px;
}
.nav-arrow:hover {
  color: var(--accent);
  border-color: var(--accent);
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--space-3);
}
.home-indices {
  margin-top: var(--space-6);
}
.idx-skeleton {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}
.scroll-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: var(--space-7);
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 600;
}
.chev {
  animation: bob 1.6s ease-in-out infinite;
}
@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(3px); }
}
@media (max-width: 767px) {
  .idx-skeleton {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
