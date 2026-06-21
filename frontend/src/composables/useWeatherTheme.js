import { ref, computed } from 'vue'
import { stocksApi } from '@/api/stocks'

import bgClean from '@/assets/backgrounds/clean.png'
import bgSunny from '@/assets/backgrounds/sunny.png'
import bgCloudy from '@/assets/backgrounds/cloudy.png'
import bgRainy from '@/assets/backgrounds/rainy.png'
import bgStormy from '@/assets/backgrounds/stormy.png'

const bgMap = {
  VERY_SUNNY: bgClean,
  SUNNY: bgSunny,
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
    return { 
      backgroundImage: weather.value ? `url(${bgMap[weather.value.weather_status]})` : 'none' 
    }
  })

  return {
    weather,
    fetchWeather,
    themeClass,
    bgStyle,
  }
}
