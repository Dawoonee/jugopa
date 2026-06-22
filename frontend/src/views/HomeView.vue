<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { stocksApi } from '@/api/stocks'
import { newsApi } from '@/api/news'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { formatDate } from '@/utils/format'
import { useWeatherTheme } from '@/composables/useWeatherTheme'
import { animalMap } from '@/constants/animals'
import MarketIndexGrid from '@/components/MarketIndexGrid.vue'
import MarketMoodBanner from '@/components/MarketMoodBanner.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import SectorCard from '@/components/SectorCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const user = computed(() => auth.user)

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
    if (auth.isAuthenticated) {
      await auth.fetchProfile().catch(() => {})
    }
  } finally {
    loading.value = false
  }
})

function getAnimalImage(code) {
  return new URL(`../assets/animal/${code}.png`, import.meta.url).href
}

function startTest() {
  if (!auth.isAuthenticated) {
    toast.show('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }
  router.push({ name: 'investment-test' })
}
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

    <!-- 생존 동물 성향 테스트 배너 -->
    <section class="home-animal card animal-card">
      <div v-if="user?.investment_type" class="animal-result">
        <div class="animal-header">
          <h2 class="block-title">나의 생존 동물</h2>
          <BaseButton variant="outline" @click="startTest">다시 하기</BaseButton>
        </div>
        <div class="animal-content">
          <div class="animal-image-wrap">
            <img :src="getAnimalImage(user.investment_type)" class="animal-img" />
          </div>
          <div class="animal-info">
            <h3 class="animal-name">{{ animalMap[user.investment_type]?.name }}</h3>
            <p class="animal-desc">{{ animalMap[user.investment_type]?.desc }}</p>
          </div>
        </div>
      </div>
      <div v-else class="animal-cta with-image">
        <div class="cta-left">
          <div class="cta-img-wrap">
            <img src="@/assets/test_card.png" alt="테스트 카드" class="cta-img" />
          </div>
          <div class="cta-text">
            <h2 class="block-title">야생의 주식장, 나의 생존 동물은?</h2>
            <p>내 주식 성향을 찰떡같은 동물로 알아보세요!</p>
          </div>
        </div>
        <BaseButton @click="startTest">테스트 시작하기</BaseButton>
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
  .animal-content {
    flex-direction: column;
    text-align: center;
  }
  .animal-cta {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
  }
}

/* 동물 테스트 카드 */
.home-animal {
  margin-top: var(--space-5);
}
.animal-card {
  padding: var(--space-5);
}
.animal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}
.animal-header .block-title {
  margin: 0;
}
.animal-content {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  background-color: #f8fafc;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}
.animal-image-wrap {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #ffffff;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.animal-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.animal-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.animal-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--primary);
  margin: 0;
}
.animal-desc {
  font-size: 14px;
  line-height: 1.4;
  color: var(--text-secondary);
  margin: 0;
}
.animal-cta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f0fdf4;
  padding: var(--space-5);
  border-radius: var(--radius-lg);
}
.animal-cta.with-image {
  flex-direction: row;
}
.cta-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.cta-img-wrap {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #ffffff;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.cta-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cta-text p {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}
@media (max-width: 767px) {
  .idx-skeleton {
    grid-template-columns: repeat(2, 1fr);
  }
  .sector-skeleton, .card-grid {
    grid-template-columns: 1fr;
  }
  .animal-content {
    flex-direction: column;
    text-align: center;
  }
  .animal-cta, .cta-left {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
  }
}
</style>
