<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { newsApi } from '@/api/news'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const router = useRouter()

const card = ref(null)
const loading = ref(true)

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

onMounted(async () => {
  try {
    const { data } = await newsApi.cardNewsDetail(route.params.id)
    card.value = data
    await fetchWeather()
  } catch (e) {
    card.value = null
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR')
}
</script>

<template>
  <div class="page card-news" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <button class="back" type="button" @click="router.back()">‹ 뒤로</button>

    <div v-if="loading" class="card">
      <Skeleton height="22px" width="50%" />
      <div style="height: 16px" />
      <Skeleton v-for="n in 4" :key="n" height="18px" />
    </div>

    <EmptyState v-else-if="!card" icon="📰" title="카드뉴스를 찾을 수 없어요" />

    <template v-else>
      <header class="news-head card">
        <div class="head-meta">
          <span class="rank">#{{ card.rank }}</span>
          <span class="sector">{{ card.sector_name }}</span>
          <span class="date num">{{ formatDate(card.target_date) }} · 기사 {{ card.article_count }}건</span>
        </div>
        <h1 class="headline">{{ card.headline }}</h1>
      </header>

      <section class="card body">
        <h2 class="block-title">전문</h2>
        <p class="summary">{{ card.summary }}</p>
      </section>

      <section v-if="card.key_points?.length" class="card points">
        <h2 class="block-title">핵심 포인트</h2>
        <ul class="point-list">
          <li v-for="(p, i) in card.key_points" :key="i" class="point">
            <span class="dot">•</span><span>{{ p }}</span>
          </li>
        </ul>
      </section>

      <section v-if="card.representative_articles?.length" class="card sources">
        <h2 class="block-title">원문 기사</h2>
        <ul class="source-list">
          <li v-for="(a, i) in card.representative_articles" :key="i">
            <a :href="a.link" target="_blank" rel="noopener" class="source">
              <span class="source-title">{{ a.title }}</span>
              <span class="source-meta">{{ a.source }} ›</span>
            </a>
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
.news-head {
  margin-bottom: var(--space-5);
}
.head-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: var(--space-3);
}
.rank {
  font-size: 12px;
  font-weight: 800;
  color: var(--accent);
}
.sector {
  font-size: 13px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: var(--accent-soft);
  color: var(--accent);
}
.date {
  font-size: 12px;
  color: var(--text-tertiary);
}
.headline {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.4;
}
.body {
  margin-bottom: var(--space-4);
}
.block-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: var(--space-3);
}
.summary {
  color: var(--text-secondary);
  line-height: 1.9;
  white-space: pre-line;
}
.points {
  margin-bottom: var(--space-4);
}
.point-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.point {
  display: flex;
  gap: 8px;
  line-height: 1.7;
}
.dot {
  color: var(--accent);
  font-weight: 800;
}
.source-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.source {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  transition: border-color var(--dur-fast);
}
.source:hover {
  border-color: var(--accent);
}
.source-title {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.source-meta {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
