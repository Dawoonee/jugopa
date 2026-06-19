<script setup>
defineProps({
  weather: { type: Object, default: null }, // { weather_status, weather_emoji, message }
})

const moodMap = {
  SUNNY: { title: '오늘은 맑음 ☀️', tone: 'sunny' },
  CLOUDY: { title: '구름 조금 ☁️', tone: 'cloudy' },
  RAINY: { title: '비 소식 🌧️', tone: 'rainy' },
  SNOWY: { title: '눈 내림 ❄️', tone: 'snowy' },
  STORMY: { title: '폭풍주의 ⚡', tone: 'stormy' },
}
function mood(status) {
  return moodMap[status] || { title: '시장 분석 중', tone: 'cloudy' }
}
</script>

<template>
  <div v-if="weather" class="mood" :class="`mood--${mood(weather.weather_status).tone}`">
    <div class="emoji">{{ weather.weather_emoji }}</div>
    <div class="mood-text">
      <p class="mood-title">{{ mood(weather.weather_status).title }}</p>
      <p class="mood-msg">{{ weather.message }}</p>
    </div>
  </div>
</template>

<style scoped>
.mood {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  background: radial-gradient(120% 120% at 0% 0%, var(--bg-elevated), var(--bg-surface));
  border: 1px solid var(--border-subtle);
}
.emoji {
  font-size: 64px;
  line-height: 1;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.4));
  animation: float 3.5s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.mood-title {
  font-size: 22px;
  font-weight: 800;
}
.mood-msg {
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}
.mood--sunny { box-shadow: inset 0 0 0 1px rgba(245, 180, 80, 0.25); }
.mood--stormy { box-shadow: inset 0 0 0 1px rgba(240, 68, 82, 0.25); }
@media (max-width: 767px) {
  .mood {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
    padding: var(--space-5);
  }
}
</style>
