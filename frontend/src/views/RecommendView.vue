<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { newsApi } from '@/api/news'
import { useAuthStore } from '@/stores/auth'
import SectorCard from '@/components/SectorCard.vue'
import StockListRow from '@/components/StockListRow.vue'
import StockSearchBar from '@/components/StockSearchBar.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const auth = useAuthStore()
const cards = ref([])
const loading = ref(true)

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

const interestSectors = ref([]) // [{id, name}]
const activeSector = ref(null)
const sectorStocks = ref([])
const stocksLoading = ref(false)
const displayedStocks = computed(() => {
  return sectorStocks.value.slice(0, 5)
})

onMounted(async () => {
  try {
    const { data } = await newsApi.sectorsToday()
    cards.value = data
    await fetchWeather()
  } finally {
    loading.value = false
  }
  await loadInterest()
})

async function loadInterest() {
  if (!auth.isAuthenticated) {
    await auth.fetchProfile().catch(() => {})
  }
  const profile = auth.user
  if (!profile?.interest_sectors?.length) return
  // interest_sectors = [id...], interest_sector_names = [name...]
  interestSectors.value = profile.interest_sectors.map((id, i) => ({
    id,
    name: profile.interest_sector_names?.[i] || `업종 ${id}`,
  }))
  activeSector.value = interestSectors.value[0]?.id ?? null
}

watch(activeSector, async (id) => {
  if (id == null) return
  stocksLoading.value = true
  try {
    const { data } = await newsApi.sectorStocks(id)
    sectorStocks.value = data.stocks
  } catch (e) {
    sectorStocks.value = []
  } finally {
    stocksLoading.value = false
  }
})
</script>

<template>
  <div class="page recommend" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <RouterLink :to="{ name: 'home' }" class="nav-arrow left" aria-label="메인 페이지">‹</RouterLink>
    <header class="rec-head">
      <h1 class="rec-title">주식 추천</h1>
      <span class="badge"><span class="dot" /> 국내 시장 분석 완료</span>
    </header>

    <!-- 종목 검색 -->
    <StockSearchBar />

    <!-- 관심 업종 -->
    <section v-if="interestSectors.length" class="interest">
      <h2 class="section-title">관심 업종</h2>
      <div class="tabs">
        <button
          v-for="s in interestSectors"
          :key="s.id"
          class="tab"
          :class="{ active: activeSector === s.id }"
          type="button"
          @click="activeSector = s.id"
        >
          {{ s.name }}
        </button>
      </div>
      <div class="card stock-list">
        <div v-if="stocksLoading" class="list-skeleton">
          <Skeleton v-for="n in 3" :key="n" height="52px" radius="var(--radius-md)" />
        </div>
        <EmptyState v-else-if="!sectorStocks.length" icon="📭" title="등록된 종목이 없어요" />
        <template v-else>
          <StockListRow v-for="s in displayedStocks" :key="s.stock_code" :stock="s" />
          <div v-if="sectorStocks.length > 5" class="more-wrap">
            <RouterLink :to="{ name: 'sector-detail', params: { id: activeSector } }" class="more-btn">
              더보기
            </RouterLink>
          </div>
        </template>
      </div>
    </section>

    <!-- 추천 섹터 -->
    <section class="sectors">
      <h2 class="section-title">관심 기반 추천 업종</h2>
      <div v-if="loading" class="sector-skeleton">
        <Skeleton v-for="n in 3" :key="n" height="260px" radius="var(--radius-lg)" />
      </div>
      <EmptyState v-else-if="!cards.length" icon="📰" title="추천 섹터가 아직 없어요" />
      <div v-else class="card-grid">
        <SectorCard v-for="c in cards.slice(0, 3)" :key="c.sector_name" :card="c" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.page.recommend {
  min-height: 100vh;
  transition: color 0.5s ease;
}
.rec-head {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: var(--space-6);
}
.eyebrow {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--accent);
  color: #ffffff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}
.rec-title {
  font-size: 28px;
  font-weight: 800;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  font-size: 12px;
  color: var(--text-secondary);
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse 1.6s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(21, 196, 126, 0.5); }
  100% { box-shadow: 0 0 0 8px rgba(21, 196, 126, 0); }
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--space-3);
}
.interest {
  margin-bottom: var(--space-6);
}
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: var(--space-3);
  flex-wrap: wrap;
}
.tab {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 14px;
}
.tab.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
.stock-list {
  padding: var(--space-2);
}
.list-skeleton {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: var(--space-2);
}
.sector-skeleton, .card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  padding-bottom: var(--space-3);
}
@media (max-width: 767px) {
  .sector-skeleton, .card-grid {
    grid-template-columns: 1fr;
  }
}
.more-wrap {
  padding: var(--space-2) 0 0;
  display: flex;
  justify-content: center;
}
.more-btn {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 16px;
  border-radius: var(--radius-pill);
  transition: background 0.2s, color 0.2s;
}
.more-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
