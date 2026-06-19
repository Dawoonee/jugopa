import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { tokenStore } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!tokenStore.access)

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
    tokenStore.clear()
    user.value = null
  }

  return { user, isAuthenticated, login, signup, fetchProfile, logout }
})
