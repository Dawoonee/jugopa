import { ref, computed } from 'vue'
import { stocksApi } from '@/api/stocks'

import bgClean from '@/assets/backgrounds/clean.png'
import bgSunny from '@/assets/backgrounds/sunny.png'
import bgCloudy from '@/assets/backgrounds/cloudy.png'
import bgRainy from '@/assets/backgrounds/rainy.png'
import bgStormy from '@/assets/backgrounds/stormy.png'

const bgMap = {
  VERY_SUNNY: bgSunny,
  SUNNY: bgClean,
  CLOUDY: bgCloudy,
  RAINY: bgRainy,
  STORMY: bgStormy,
}

const themeMap = {
  VERY_SUNNY: 'theme-light',
  SUNNY: 'theme-light',
  CLOUDY: 'theme-light',
  RAINY: 'theme-dark',
  STORMY: 'theme-dark',
}

export function useWeatherTheme() {
  const weather = ref(null)
  
  const fetchWeather = async () => {
    try {
      const { data } = await stocksApi.weatherToday()
      weather.value = data
    } catch (e) {
      console.error('Failed to fetch weather', e)
    }
  }

  const themeClass = computed(() => {
    return weather.value ? themeMap[weather.value.weather_status] : 'theme-light'
  })

  const bgStyle = computed(() => {
    // 날씨 데이터가 없거나(404·네트워크 실패) 알 수 없는 상태면 기본 배경(clean)으로 폴백 — 흰 화면 방지
    const bg = (weather.value && bgMap[weather.value.weather_status]) || bgClean
    return {
      backgroundImage: `url(${bg})`
    }
  })

  return {
    weather,
    fetchWeather,
    themeClass,
    bgStyle,
  }
}
