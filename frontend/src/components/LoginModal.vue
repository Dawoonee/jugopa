<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) return
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    toast.show('로그인되었어요', 'success')
    auth.showLoginModal = false
    // If there's a redirect query, we could push it, but we removed /login route.
    // If they were on home, they stay on home.
  } catch (e) {
    toast.show('아이디 또는 비밀번호를 확인해 주세요', 'error')
  } finally {
    loading.value = false
  }
}

function close() {
  auth.showLoginModal = false
}

function goSignup() {
  auth.showLoginModal = false
  router.push({ name: 'signup' })
}
</script>

<template>
  <div class="modal-overlay" @click.self="close">
    <div class="auth-card card">
      <button class="close-btn" @click="close" aria-label="닫기">
        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>

      <h1 class="auth-title">로그인</h1>
      <p class="auth-sub">주식 고수가 되고파, 주고파</p>

      <form class="auth-form" @submit.prevent="submit">
        <BaseInput v-model="username" label="아이디" placeholder="아이디" autocomplete="username" />
        <BaseInput
          v-model="password"
          label="비밀번호"
          type="password"
          placeholder="비밀번호"
          autocomplete="current-password"
        />
        <BaseButton type="submit" block :disabled="loading || !username || !password">
          {{ loading ? '로그인 중…' : '로그인' }}
        </BaseButton>
      </form>

      <p class="auth-foot">
        아직 회원이 아니신가요?
        <button type="button" @click="goSignup" class="link">회원가입</button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  padding: var(--space-4);
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; backdrop-filter: blur(0); }
  to { opacity: 1; backdrop-filter: blur(8px); }
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6) var(--space-5);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  transition: color 0.2s, background 0.2s;
}

.close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.auth-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
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
