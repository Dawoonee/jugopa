<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stocksApi } from '@/api/stocks'
import { communityApi } from '@/api/community'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { formatNumber, formatSignedNumber, formatSignedRate, changeClass } from '@/utils/format'
import DayRangeDoughnut from '@/components/DayRangeDoughnut.vue'
import PriceVolumeCombo from '@/components/PriceVolumeCombo.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const stock = ref(null)
const loading = ref(true)
const bookmarked = ref(false)
const previewPosts = ref([])

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

// 최근 → 과거 순으로 와도 차트는 오래된 → 최신 정렬
const prices = computed(() => {
  if (!stock.value?.daily_prices) return []
  return [...stock.value.daily_prices].sort((a, b) => a.record_date.localeCompare(b.record_date))
})
const labels = computed(() => prices.value.map((p) => p.record_date.slice(5)))
const closes = computed(() => prices.value.map((p) => p.close_price))
const volumes = computed(() => prices.value.map((p) => p.volume))

const latest = computed(() => prices.value[prices.value.length - 1] || null)
const change = computed(() => (latest.value ? latest.value.close_price - latest.value.open_price : 0))
const changeRate = computed(() =>
  latest.value && latest.value.open_price ? (change.value / latest.value.open_price) * 100 : 0,
)
const naverNewsUrl = computed(
  () => `https://finance.naver.com/item/news.naver?code=${stock.value?.stock_code ?? ''}`,
)

onMounted(async () => {
  const code = route.params.code
  try {
    const { data } = await stocksApi.detail(code)
    stock.value = data
    await fetchWeather()
  } catch (e) {
    toast.show('종목 정보를 불러오지 못했어요', 'error')
  } finally {
    loading.value = false
  }
  try {
    const { data } = await communityApi.posts(code)
    previewPosts.value = data.slice(0, 3)
  } catch (e) {
    previewPosts.value = []
  }
  if (auth.isAuthenticated) {
    try {
      const { data } = await stocksApi.bookmarks()
      bookmarked.value = data.some((b) => b.stock_code === code)
    } catch (e) {
      /* noop */
    }
  }
})

async function toggleBookmark() {
  if (!auth.isAuthenticated) {
    toast.show('로그인이 필요해요', 'error')
    return
  }
  const code = route.params.code
  try {
    if (bookmarked.value) {
      await stocksApi.removeBookmark(code)
      bookmarked.value = false
      toast.show('관심 종목에서 제외했어요')
    } else {
      await stocksApi.addBookmark(code)
      bookmarked.value = true
      toast.show('관심 종목에 추가했어요', 'success')
    }
  } catch (e) {
    toast.show('처리에 실패했어요', 'error')
  }
}
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

    <template v-else-if="stock">
      <header class="detail-head">
        <div>
          <h1 class="stock-name">{{ stock.stock_name }}</h1>
          <span class="stock-code num">{{ stock.stock_code }} · {{ stock.market_type }}</span>
        </div>
        <div class="head-actions">
          <a class="news-link" :href="naverNewsUrl" target="_blank" rel="noopener noreferrer">
            📰 뉴스·공시
          </a>
          <BaseButton :variant="bookmarked ? 'primary' : 'outline'" @click="toggleBookmark">
            {{ bookmarked ? '♥ 관심' : '♡ 관심' }}
          </BaseButton>
        </div>
      </header>

      <section v-if="latest" class="price-card card">
        <span class="cur num">{{ formatNumber(latest.close_price) }}<small>원</small></span>
        <span class="chg num" :class="changeClass(changeRate)">
          {{ formatSignedNumber(change) }} ({{ formatSignedRate(changeRate) }})
        </span>
        <span class="vol num">거래량 {{ formatNumber(latest.volume) }}</span>
      </section>

      <section class="charts">
        <div v-if="latest" class="chart-card card doughnut-card">
          <h3 class="chart-title">당일 시세 변동</h3>
          <DayRangeDoughnut
            :high="latest.high_price"
            :low="latest.low_price"
            :close="latest.close_price"
          />
        </div>
        <div class="chart-card card combo-card">
          <h3 class="chart-title">최근 30일 종가 · 거래량</h3>
          <PriceVolumeCombo :labels="labels" :closes="closes" :volumes="volumes" />
        </div>
      </section>

      <section class="comm-card card">
        <div class="comm-head">
          <h3 class="comm-title">커뮤니티</h3>
          <RouterLink :to="{ name: 'stock-community', params: { code: stock.stock_code } }" class="more">
            더보기 ›
          </RouterLink>
        </div>
        <p v-if="!previewPosts.length" class="empty-line">아직 글이 없어요. 첫 글을 남겨보세요!</p>
        <ul v-else class="preview-list">
          <li v-for="p in previewPosts" :key="p.id">
            <RouterLink
              :to="{ name: 'community-post-detail', params: { code: stock.stock_code, postId: p.id } }"
              class="preview-item"
            >
              <span class="preview-title">{{ p.title || p.content }}</span>
              <span class="preview-meta num">♥ {{ p.like_count }} · 💬 {{ p.comment_count }}</span>
            </RouterLink>
          </li>
        </ul>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}
.stock-name {
  font-size: 24px;
  font-weight: 800;
}
.stock-code {
  font-size: 13px;
  color: var(--text-tertiary);
}
.head-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.news-link {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  transition: color var(--dur-fast), background var(--dur-fast);
}
.news-link:hover {
  color: var(--accent);
  background: var(--bg-elevated);
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
.cur small {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-left: 4px;
}
.chg {
  font-size: 15px;
  font-weight: 700;
}
.vol {
  font-size: 13px;
  color: var(--text-tertiary);
}
.charts {
  display: grid;
  grid-template-columns: minmax(0, 280px) minmax(0, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
@media (max-width: 720px) {
  .charts {
    grid-template-columns: 1fr;
  }
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
.comm-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.comm-title {
  font-size: 16px;
  font-weight: 700;
}
.more {
  color: var(--accent);
  font-size: 13px;
  font-weight: 600;
}
.empty-line {
  color: var(--text-tertiary);
  font-size: 14px;
}
.preview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.preview-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  margin: 0 -10px;
  border-radius: var(--radius-sm);
  color: inherit;
  transition: background var(--dur-fast);
}
.preview-item:hover {
  background: var(--bg-elevated);
}
.preview-item:hover .preview-title {
  color: var(--accent);
}
.preview-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}
.preview-meta {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
