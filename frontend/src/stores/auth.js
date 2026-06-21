import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { tokenStore } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  // localStorage 값으로 초기화 → 새로고침/앱 시작 시에도 정확
  const accessToken = ref(tokenStore.access)
  const isAuthenticated = computed(() => !!accessToken.value)

  // localStorage(tokenStore) 변경 시 반응형 상태 동기화
  // 로그인/로그아웃뿐 아니라 인터셉터의 토큰 재발급·만료까지 반영
  tokenStore.subscribe(() => {
    accessToken.value = tokenStore.access
    if (!accessToken.value) user.value = null
  })

  async function login(username, password) {
    const { data } = await authApi.login({ username, password })
    tokenStore.set({ access: data.access, refresh: data.refresh })
    await fetchProfile()
  }

  async function signup(payload) {
    await authApi.signup(payload)
    // 가입 후 자동 로그인
    await login(payload.username, payload.password)
  }

  async function fetchProfile() {
    if (!tokenStore.access) return null
    const { data } = await authApi.getProfile()
    user.value = data
    return data
  }

  function logout() {
    // clear() → subscribe 콜백이 accessToken/user 상태를 정리
    tokenStore.clear()
  }

  return { user, isAuthenticated, login, signup, fetchProfile, logout }
})
