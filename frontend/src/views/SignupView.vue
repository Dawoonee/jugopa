<script setup>
import { ref, computed, onMounted } from 'vue'
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
const passwordConfirm = ref('')
const sectors = ref([])
const selected = ref(new Set())
const loading = ref(false)

// 두 비밀번호가 모두 입력됐는데 서로 다를 때만 경고 표시
const passwordMismatch = computed(
  () => !!passwordConfirm.value && form.value.password !== passwordConfirm.value,
)

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
