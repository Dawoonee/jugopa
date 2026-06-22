<script setup>
import { ref, onMounted } from 'vue'
import { stocksApi } from '@/api/stocks'
import { newsApi } from '@/api/news'
import { formatDate } from '@/utils/format'
import { useWeatherTheme } from '@/composables/useWeatherTheme'
import MarketIndexGrid from '@/components/MarketIndexGrid.vue'
import MarketMoodBanner from '@/components/MarketMoodBanner.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import SectorCard from '@/components/SectorCard.vue'

const indices = ref([])
const recommendCards = ref([])
const loading = ref(true)
const today = formatDate()

const { weather, fetchWeather, themeClass, bgStyle } = useWeatherTheme()

onMounted(async () => {
  try {
    const [idxRes, newsRes] = await Promise.allSettled([
      stocksApi.indices(),
      newsApi.sectorsToday()
    ])
    if (idxRes.status === 'fulfilled') indices.value = idxRes.value.data
    if (newsRes.status === 'fulfilled') recommendCards.value = newsRes.value.data
    
    await fetchWeather()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div 
    class="page home" 
    :class="themeClass"
  >
    <div class="weather-bg" :style="bgStyle"></div>
    <header class="home-head">
      <RouterLink :to="{ name: 'knowledge' }" class="nav-arrow left" aria-label="경제 지식">‹</RouterLink>
      <p class="home-date">{{ today }}</p>
      <RouterLink :to="{ name: 'recommend' }" class="nav-arrow right" aria-label="주식 추천">›</RouterLink>
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

    <!-- 관심 기반 추천 업종 -->
    <section class="home-sectors">
      <h2 class="section-title">관심 기반 추천 업종</h2>
      <div v-if="loading" class="sector-skeleton">
        <Skeleton v-for="n in 3" :key="n" height="260px" radius="var(--radius-lg)" />
      </div>
      <div v-else-if="recommendCards.length" class="card-grid">
        <SectorCard v-for="c in recommendCards.slice(0, 3)" :key="c.sector_name" :card="c" />
      </div>
    </section>

  </div>
</template>

<style scoped>
.page.home {
  min-height: 100vh;
  transition: color 0.5s ease;
}

.home-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  margin-bottom: var(--space-5);
  padding-top: var(--space-3);
  height: 60px;
}
.home-date {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  pointer-events: none;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--space-3);
}
.home-indices {
  margin-top: var(--space-6);
}
.home-sectors {
  margin-top: var(--space-6);
}
.sector-skeleton {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  padding-bottom: var(--space-3);
}
.idx-skeleton {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}
@media (max-width: 767px) {
  .idx-skeleton {
    grid-template-columns: repeat(2, 1fr);
  }
  .sector-skeleton, .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
