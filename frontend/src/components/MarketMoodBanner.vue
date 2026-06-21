<script setup>
defineProps({
  weather: { type: Object, default: null }, // { weather_status, weather_emoji, message }
})

const moodMap = {
  VERY_SUNNY: { title: '매우 맑음 ☀️', tone: 'very_sunny' },
  SUNNY: { title: '오늘은 맑음 🌤️', tone: 'sunny' },
  CLOUDY: { title: '흐림 ☁️', tone: 'cloudy' },
  RAINY: { title: '비 🌧️', tone: 'rainy' },
  STORMY: { title: '비+천둥 ⛈️', tone: 'stormy' },
}
function mood(status) {
  return moodMap[status] || { title: '시장 분석 중 ☁️', tone: 'cloudy' }
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
  /* Glassmorphism Effect */
  background: var(--glass-bg, rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.3));
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
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
  color: inherit;
  opacity: 0.85;
  font-size: 14px;
  line-height: 1.6;
}
@media (max-width: 767px) {
  .mood {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
    padding: var(--space-5);
  }
}
</style>
