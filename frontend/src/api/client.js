import axios from 'axios'

const ACCESS_KEY = 'jugopa_access'
const REFRESH_KEY = 'jugopa_refresh'

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
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

const client = axios.create({
  baseURL: '/api/v1',
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
          axios.post('/api/v1/accounts/token/refresh/', { refresh: tokenStore.refresh })
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
