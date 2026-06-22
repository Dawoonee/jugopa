<script setup>
defineProps({
  weather: { type: Object, default: null }, // { weather_status, weather_emoji, message, score? }
})

const moodMap = {
  VERY_SUNNY: { title: '매우 맑음 ☀️', tone: 'very_sunny', score: 100 },
  SUNNY: { title: '오늘은 맑음 🌤️', tone: 'sunny', score: 75 },
  CLOUDY: { title: '흐림 ☁️', tone: 'cloudy', score: 50 },
  RAINY: { title: '비 🌧️', tone: 'rainy', score: 25 },
  STORMY: { title: '비+천둥 ⛈️', tone: 'stormy', score: 0 },
}
function mood(status) {
  return moodMap[status] || { title: '시장 분석 중 ☁️', tone: 'cloudy', score: 50 }
}

function diffClass(diff) {
  if (diff >= 2.0) return 'diff--hot'
  if (diff <= -2.0) return 'diff--cold'
  if (diff > 0) return 'diff--warm'
  if (diff < 0) return 'diff--cool'
  return 'diff--neutral'
}
</script>

<template>
  <div v-if="weather" class="mood" :class="`mood--${mood(weather.weather_status).tone}`">
    <div class="mood-left">
      <div class="emoji">{{ weather.weather_emoji }}</div>
      <div class="mood-text">
        <p class="mood-title">{{ mood(weather.weather_status).title }}</p>
        <p class="mood-msg">{{ weather.message }}</p>
      </div>
    </div>

    <div class="mood-right">
      <div class="gauge-grid">
        <span class="gauge-icon">☀️</span>
        <div class="gauge-track">
          <!-- indicator arrow -->
          <div 
            class="gauge-indicator" 
            :style="{ left: `${100 - (weather.score ?? mood(weather.weather_status).score)}%` }"
          ></div>
        </div>
        <span class="gauge-icon sun-icon">⛈️</span>
        <div class="gauge-label">맑음 수치 ({{ weather.score ?? mood(weather.weather_status).score }}%)</div>
      </div>
    </div>
  </div>

  <div v-if="weather && weather.temp_diff !== undefined" class="diff-banner" :class="diffClass(weather.temp_diff)">
    <div class="diff-header">
      <span class="diff-temp">{{ weather.temp_diff > 0 ? '+' : '' }}{{ weather.temp_diff }}°C</span>
      <h4 class="diff-title">{{ weather.diff_title }}</h4>
    </div>
    <p class="diff-msg">{{ weather.diff_msg }}</p>
  </div>
</template>

<style scoped>
.mood {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
  padding: var(--space-5) var(--space-6);
  border-radius: var(--radius-xl);
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.mood-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.emoji {
  font-size: 56px;
  line-height: 1;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
  animation: float 3.5s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.mood-text {
  color: #1a1a1a;
}
.mood-title {
  font-size: 20px;
  font-weight: 800;
}
.mood-msg {
  margin-top: 4px;
  color: #6b7684;
  font-size: 14px;
  line-height: 1.5;
}

.mood-right {
  flex: 1;
  max-width: 450px;
  margin-left: auto;
}

.gauge-grid {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0 12px;
}

.gauge-icon {
  font-size: 32px;
  line-height: 1;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.1));
}
.sun-icon {
  font-size: 36px;
}

.gauge-track {
  position: relative;
  height: 24px;
  border-radius: 12px;
  background: linear-gradient(to right, #dd6b20 0%, #ed8936 20%, #f6ad55 40%, #fbd38d 70%, #e2e8f0 100%);
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.gauge-indicator {
  position: absolute;
  bottom: -10px;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 10px solid #dd6b20;
  transform: translateX(-50%);
  transition: left 1s cubic-bezier(0.16, 1, 0.3, 1);
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.gauge-label {
  grid-column: 2;
  margin-top: 12px;
  font-size: 13px;
  font-weight: 700;
  color: #4e5968;
}

@media (max-width: 767px) {
  .mood {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    gap: var(--space-5);
  }
  .mood-left {
    flex-direction: column;
  }
  .mood-right {
    max-width: 100%;
    margin-left: 0;
  }
  .gauge-label {
    text-align: left;
}
  .diff-banner {
    flex-direction: column;
    text-align: left;
    align-items: flex-start;
  }
}

/* 온도차 배너 스타일 */
.diff-banner {
  margin-top: var(--space-4);
  padding: var(--space-5) var(--space-6);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}
.diff-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.diff-temp {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
}
.diff-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}
.diff-msg {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
  line-height: 1.4;
}

/* 온도차에 따른 색상 테마 (글자색만 적용) */
.diff--hot {
  color: #c53030;
}
.diff--warm {
  color: #c05621;
}
.diff--cool {
  color: #166534;
}
.diff--cold {
  color: #2b6cb0;
}
.diff--neutral {
  color: #475569;
}
</style>
