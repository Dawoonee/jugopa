<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { authApi } from '@/api/auth'
import { newsApi } from '@/api/news'
import { useWeatherTheme } from '@/composables/useWeatherTheme'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import TagChip from '@/components/common/TagChip.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const form = ref({ username: '', password: '', email: '', nickname: '' })
const passwordConfirm = ref('')
const sectors = ref([])
const selected = ref(new Set())
const loading = ref(false)

// 두 비밀번호가 모두 입력됐는데 서로 다를 때만 경고 표시
const passwordMismatch = computed(
  () => !!passwordConfirm.value && form.value.password !== passwordConfirm.value,
)

const { weather, fetchWeather, themeClass, bgStyle } = useWeatherTheme()

onMounted(async () => {
  document.body.style.overflow = 'hidden'
  try {
    const { data } = await newsApi.sectors()
    sectors.value = data
  } catch (e) {
    sectors.value = []
  }
  await fetchWeather()
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})

function toggleSector(id) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
  selected.value = new Set(selected.value)
}

async function recommendPassword() {
  try {
    const { data } = await authApi.randomPassword()
    // 추천 비밀번호는 직접 타이핑한 게 아니므로 확인 칸도 함께 채워준다
    form.value.password = data.recommended_password
    passwordConfirm.value = data.recommended_password
    toast.show('안전한 비밀번호를 추천했어요', 'success')
  } catch (e) {
    toast.show('비밀번호 추천에 실패했어요', 'error')
  }
}

async function submit() {
  if (form.value.password !== passwordConfirm.value) {
    toast.show('비밀번호가 일치하지 않아요', 'error')
    return
  }
  loading.value = true
  try {
    await auth.signup({ ...form.value, interest_sectors: [...selected.value] })
    toast.show('가입을 환영해요! 🎉', 'success')
    router.push({ name: 'home' })
  } catch (e) {
    const msg = e.response?.data ? Object.values(e.response.data).flat()[0] : '가입에 실패했어요'
    toast.show(String(msg), 'error')
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push({ name: 'home' })
  auth.showLoginModal = true
}
</script>

<template>
  <div class="auth page" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <div class="modal-overlay">
      <div class="auth-card login-card card">
      <h1 class="auth-title">회원가입</h1>
      <p class="auth-sub">관심 업종을 고르면 맞춤 추천을 받을 수 있어요</p>

      <form class="auth-form" @submit.prevent="submit">
        <BaseInput v-model="form.username" label="아이디" placeholder="아이디" />
        <BaseInput v-model="form.nickname" label="닉네임" placeholder="닉네임" />
        <BaseInput v-model="form.email" label="이메일" type="email" placeholder="example@email.com" />

        <div class="pw-row">
          <BaseInput v-model="form.password" label="비밀번호" type="password" placeholder="비밀번호" />
          <BaseButton variant="outline" type="button" @click="recommendPassword">추천</BaseButton>
        </div>

        <div>
          <BaseInput
            v-model="passwordConfirm"
            label="비밀번호 확인"
            type="password"
            placeholder="비밀번호를 한 번 더 입력하세요"
          />
          <p v-if="passwordMismatch" class="pw-error">비밀번호가 일치하지 않아요</p>
        </div>

        <div class="sectors">
          <span class="sectors-label">관심 업종 (복수 선택)</span>
          <div class="sectors-grid">
            <button
              v-for="s in sectors"
              :key="s.id"
              type="button"
              class="sector-pick"
              @click="toggleSector(s.id)"
            >
              <TagChip :label="s.name" :active="selected.has(s.id)" clickable />
            </button>
          </div>
        </div>

        <BaseButton type="submit" block :disabled="loading || passwordMismatch">
          {{ loading ? '가입 중…' : '가입하기' }}
        </BaseButton>
      </form>

      <p class="auth-foot">
        이미 계정이 있으신가요?
        <button type="button" @click="goLogin" class="link">로그인</button>
      </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth {
  min-height: 100vh;
  transition: color 0.5s ease;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.4);
  padding: var(--space-4);
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.auth-card.login-card {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: var(--space-6) var(--space-5);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid var(--border-strong);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.auth-title {
  font-size: 26px;
  font-weight: 800;
}
.auth-sub {
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}
.auth-form {
  margin-top: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.pw-row {
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
}
.pw-row :deep(.field) {
  flex: 1;
}
.pw-error {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--danger);
}
.sectors-label {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.sectors-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sector-pick {
  background: none;
  border: none;
  padding: 0;
}
.auth-foot {
  margin-top: var(--space-5);
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}
.link {
  background: none;
  border: none;
  padding: 0;
  color: var(--accent);
  font-weight: 700;
  cursor: pointer;
  font-size: 14px;
}
.link:hover {
  text-decoration: underline;
}
</style>

<style>
/* 전역 스코프로 로그인/회원가입 모달 스타일 제어 */
.auth-card.login-card {
  background: #ffffff !important;
  color: #1a1a1a;
  --bg-surface: #f5f7fa;
  --bg-elevated: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #6b7684;
  --text-tertiary: #8b95a1;
  --border-strong: rgba(0, 0, 0, 0.15);
  --border-subtle: rgba(0, 0, 0, 0.08);
}
.auth-card.login-card .auth-title {
  color: #1a1a1a;
}
</style>
