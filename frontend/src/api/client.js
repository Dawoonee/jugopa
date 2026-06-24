import axios from 'axios'

const ACCESS_KEY = 'jugopa_access'
const REFRESH_KEY = 'jugopa_refresh'

// 토큰 변경 구독자 (스토어가 반응형 상태를 동기화하는 데 사용)
const listeners = new Set()
function notify() {
  for (const fn of listeners) fn()
}

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
    notify()
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    notify()
  },
  subscribe(fn) {
    listeners.add(fn)
    return () => listeners.delete(fn)
  },
}

// 운영: VITE_API_BASE_URL(백엔드 절대경로), 개발: dev 프록시(`/api/v1`)
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// 요청마다 액세스 토큰 첨부
client.interceptors.request.use((config) => {
  const token = tokenStore.access
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 → refresh로 1회 재발급 후 재시도
let refreshing = null

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const { config, response } = error
    if (response?.status === 401 && !config._retried && tokenStore.refresh) {
      config._retried = true
      try {
        refreshing =
          refreshing ||
          axios.post(`${API_BASE}/accounts/token/refresh/`, { refresh: tokenStore.refresh })
        const { data } = await refreshing
        refreshing = null
        tokenStore.set({ access: data.access })
        config.headers.Authorization = `Bearer ${data.access}`
        return client(config)
      } catch (e) {
        refreshing = null
        tokenStore.clear()
      }
    }
    return Promise.reject(error)
  },
)

export default client
