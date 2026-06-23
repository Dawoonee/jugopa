<script setup>
import { ref, onMounted, reactive } from 'vue'
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
const groups = ref([]) // [{ sector_id, sector_name, stock_count, stocks: [] }]
const loading = ref(true)

// 중분류 sector_id -> 열림 여부 (아코디언 토글)
const openGroups = reactive({})

onMounted(async () => {
  await fetchWeather()
  try {
    const { data } = await newsApi.sectorBreakdown(sectorId)
    sectorName.value = data.sector_name
    groups.value = data.groups
    // 기본: 첫 그룹만 펼침
    if (data.groups.length) {
      openGroups[data.groups[0].sector_id] = true
    }
  } catch (error) {
    console.error('Failed to load sector breakdown', error)
  } finally {
    loading.value = false
  }
})

function toggleGroup(id) {
  openGroups[id] = !openGroups[id]
}

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
        <span class="info-text">중분류별 · 시가총액순</span>
      </div>

      <div v-if="loading" class="list-skeleton">
        <Skeleton v-for="n in 6" :key="n" height="56px" radius="var(--radius-md)" />
      </div>

      <EmptyState v-else-if="!groups.length" icon="📭" title="등록된 종목이 없어요" />

      <div v-else class="groups">
        <section v-for="g in groups" :key="g.sector_id" class="card group">
          <button
            class="group-head"
            type="button"
            :aria-expanded="!!openGroups[g.sector_id]"
            @click="toggleGroup(g.sector_id)"
          >
            <span class="group-title">{{ g.sector_name }}</span>
            <span class="group-meta">
              <span class="group-count">{{ g.stock_count }}</span>
              <span class="chevron" :class="{ open: openGroups[g.sector_id] }">›</span>
            </span>
          </button>

          <div v-show="openGroups[g.sector_id]" class="group-body">
            <template v-if="g.stocks.length">
              <StockListRow v-for="s in g.stocks" :key="s.stock_code" :stock="s" />
            </template>
            <p v-else class="group-empty">종목이 없어요</p>
          </div>
        </section>
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

.groups {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.group {
  padding: 0;
  overflow: hidden;
}

.group-head {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px var(--space-4);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
}

.group-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.group-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-count {
  min-width: 24px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-pill);
  padding: 2px 8px;
}

.chevron {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-tertiary);
  transform: rotate(90deg);
  transition: transform var(--dur-fast);
}

.chevron.open {
  transform: rotate(-90deg);
}

.group-body {
  padding: 0 var(--space-2) var(--space-2);
  border-top: 1px solid var(--border-subtle);
}

.group-empty {
  padding: 16px var(--space-4);
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: center;
}

.list-skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
