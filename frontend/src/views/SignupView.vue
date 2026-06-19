<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { authApi } from '@/api/auth'
import { newsApi } from '@/api/news'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import TagChip from '@/components/common/TagChip.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const form = ref({ username: '', password: '', email: '', nickname: '' })
const sectors = ref([])
const selected = ref(new Set())
const loading = ref(false)

onMounted(async () => {
  try {
    const { data } = await newsApi.sectors()
    sectors.value = data
  } catch (e) {
    sectors.value = []
  }
})

function toggleSector(id) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
  selected.value = new Set(selected.value)
}

async function recommendPassword() {
  try {
    const { data } = await authApi.randomPassword()
    form.value.password = data.recommended_password
    toast.show('안전한 비밀번호를 추천했어요', 'success')
  } catch (e) {
    toast.show('비밀번호 추천에 실패했어요', 'error')
  }
}

async function submit() {
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
</script>

<template>
  <div class="auth">
    <div class="auth-card card">
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

        <BaseButton type="submit" block :disabled="loading">
          {{ loading ? '가입 중…' : '가입하기' }}
        </BaseButton>
      </form>

      <p class="auth-foot">
        이미 계정이 있으신가요?
        <RouterLink :to="{ name: 'login' }" class="link">로그인</RouterLink>
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
  max-width: 460px;
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
  color: var(--accent);
  font-weight: 700;
}
</style>
