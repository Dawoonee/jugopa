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
    router.push(route.query.redirect || { name: 'home' })
  } catch (e) {
    toast.show('아이디 또는 비밀번호를 확인해 주세요', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="auth-card card">
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
        <RouterLink :to="{ name: 'signup' }" class="link">회원가입</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth {
  min-height: calc(100vh - var(--header-height));
  display: grid;
  place-items: center;
  padding: var(--space-5) var(--space-4);
}
.auth-card {
  width: 100%;
  max-width: 400px;
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
.auth-foot {
  margin-top: var(--space-5);
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}
.link {
  color: var(--accent);
  font-weight: 700;
}
</style>
