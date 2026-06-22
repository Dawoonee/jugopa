<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stocksApi } from '@/api/stocks'
import { formatNumber, formatSignedNumber, formatSignedRate, changeClass } from '@/utils/format'
import IndexCloseChart from '@/components/IndexCloseChart.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import { useToastStore } from '@/stores/toast'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

const detail = ref(null)
const loading = ref(true)

const history = computed(() => detail.value?.history ?? [])
const labels = computed(() => history.value.map((h) => h.base_date.slice(5)))
const closes = computed(() => history.value.map((h) => h.close_price))
const latest = computed(() => detail.value?.latest ?? null)

onMounted(async () => {
  try {
    const { data } = await stocksApi.indexDetail(route.params.name)
    detail.value = data
    await fetchWeather()
  } catch (e) {
    toast.show('지수 정보를 불러오지 못했어요', 'error')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page detail" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <button class="back" type="button" @click="router.back()">‹ 뒤로</button>

    <div v-if="loading" class="card">
      <Skeleton height="28px" width="40%" />
      <div style="height: 12px" />
      <Skeleton height="40px" width="60%" />
      <div style="height: 16px" />
      <Skeleton height="260px" radius="var(--radius-md)" />
    </div>

    <template v-else-if="detail">
      <header class="detail-head">
        <h1 class="index-name">{{ detail.index_name }}</h1>
        <span class="index-sub">시장 지수</span>
      </header>

      <section v-if="latest" class="price-card card">
        <span class="cur num">{{ formatNumber(latest.close_price, 2) }}</span>
        <span class="chg num" :class="changeClass(latest.change_rate)">
          {{ formatSignedNumber(latest.change, 2) }} ({{ formatSignedRate(latest.change_rate) }})
        </span>
        <span class="asof num">기준일 {{ latest.base_date }}</span>
      </section>

      <section class="chart-card card">
        <h3 class="chart-title">최근 30일 종가 추이</h3>
        <p v-if="!history.length" class="empty-line">표시할 시세 데이터가 아직 없어요.</p>
        <IndexCloseChart v-else :labels="labels" :closes="closes" />
      </section>
    </template>
  </div>
</template>

<style scoped>
.back {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 14px;
  margin-bottom: var(--space-4);
}
.back:hover {
  color: var(--accent);
}
.detail-head {
  margin-bottom: var(--space-4);
}
.index-name {
  font-size: 24px;
  font-weight: 800;
}
.index-sub {
  font-size: 13px;
  color: var(--text-tertiary);
}
.price-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: var(--space-4);
}
.cur {
  font-size: 34px;
  font-weight: 800;
}
.chg {
  font-size: 15px;
  font-weight: 700;
}
.asof {
  font-size: 13px;
  color: var(--text-tertiary);
}
.chart-card {
  margin-bottom: 0;
}
.chart-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}
.empty-line {
  color: var(--text-tertiary);
  font-size: 14px;
}
</style>
