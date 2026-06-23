<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { newsApi } from '@/api/news'
import StockListRow from '@/components/StockListRow.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const router = useRouter()
const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

const sectorId = route.params.id
const sectorName = ref('')
const stocks = ref([])
const loading = ref(true)

onMounted(async () => {
  await fetchWeather()
  try {
    const { data } = await newsApi.sectorStocks(sectorId)
    sectorName.value = data.sector_name
    stocks.value = data.stocks
  } catch (error) {
    console.error('Failed to load sector stocks', error)
  } finally {
    loading.value = false
  }
})

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="page sector-detail" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    
    <header class="header">
      <button class="nav-arrow left" @click="goBack" aria-label="뒤로가기">‹</button>
      <h1 class="title">{{ sectorName || '업종 상세' }}</h1>
    </header>

    <main class="content">
      <div class="info-bar">
        <span class="info-text">시가총액 기준 전체 종목</span>
      </div>

      <div class="card stock-list-card">
        <div v-if="loading" class="list-skeleton">
          <Skeleton v-for="n in 8" :key="n" height="52px" radius="var(--radius-md)" />
        </div>
        <EmptyState v-else-if="!stocks.length" icon="📭" title="등록된 종목이 없어요" />
        <template v-else>
          <StockListRow v-for="s in stocks" :key="s.stock_code" :stock="s" />
        </template>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page.sector-detail {
  min-height: 100vh;
  transition: color 0.5s ease;
  padding-top: var(--space-4);
  padding-bottom: var(--space-8);
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-6);
  position: relative;
  height: 40px;
}

.nav-arrow.left {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.title {
  width: 100%;
  text-align: center;
  font-size: 20px;
  font-weight: 800;
  margin: 0;
}

.content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.info-bar {
  display: flex;
  justify-content: flex-end;
  padding: 0 var(--space-2);
}

.info-text {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  background: var(--bg-surface);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
}

.stock-list-card {
  padding: var(--space-2);
}

.list-skeleton {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: var(--space-2);
}
</style>
