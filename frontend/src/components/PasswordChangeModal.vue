<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { authApi } from '@/api/auth'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const emit = defineEmits(['update:modelValue'])
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const currentPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const loading = ref(false)

// 새 비밀번호가 모두 입력됐는데 서로 다를 때만 경고 표시
const passwordMismatch = computed(
  () => !!newPasswordConfirm.value && newPassword.value !== newPasswordConfirm.value,
)

async function recommendPassword() {
  try {
    const { data } = await authApi.randomPassword()
    // 추천 비밀번호는 직접 타이핑한 게 아니므로 확인 칸도 함께 채워준다
    newPassword.value = data.recommended_password
    newPasswordConfirm.value = data.recommended_password
    toast.show('안전한 비밀번호를 추천했어요', 'success')
  } catch (e) {
    toast.show('비밀번호 추천에 실패했어요', 'error')
  }
}

async function submit() {
  if (newPassword.value !== newPasswordConfirm.value) {
    toast.show('비밀번호가 일치하지 않아요', 'error')
    return
  }
  loading.value = true
  try {
    await authApi.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    toast.show('비밀번호가 변경되었어요. 다시 로그인해주세요', 'success')
    auth.logout()
    emit('update:modelValue', false)
    auth.showLoginModal = true
  } catch (e) {
    const msg = e.response?.data
      ? Object.values(e.response.data).flat()[0]
      : '비밀번호 변경에 실패했어요'
    toast.show(String(msg), 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal :model-value="true" title="비밀번호 변경" @update:model-value="emit('update:modelValue', false)">
    <div class="pw-form">
      <BaseInput
        v-model="currentPassword"
        label="현재 비밀번호"
        type="password"
        placeholder="현재 비밀번호"
        autocomplete="current-password"
      />

      <div class="pw-row">
        <BaseInput
          v-model="newPassword"
          label="변경할 비밀번호"
          type="password"
          placeholder="변경할 비밀번호"
          autocomplete="new-password"
        />
        <BaseButton variant="outline" type="button" @click="recommendPassword">추천</BaseButton>
      </div>

      <div>
        <BaseInput
          v-model="newPasswordConfirm"
          label="변경할 비밀번호 다시 입력"
          type="password"
          placeholder="변경할 비밀번호를 한 번 더 입력하세요"
          autocomplete="new-password"
        />
        <p v-if="passwordMismatch" class="pw-error">비밀번호가 일치하지 않아요</p>
      </div>
    </div>
    <template #footer>
      <BaseButton
        class="foot-save"
        :disabled="loading || passwordMismatch || !currentPassword || !newPassword"
        @click="submit"
      >
        {{ loading ? '변경 중…' : '변경하기' }}
      </BaseButton>
      <BaseButton class="foot-cancel" variant="ghost" @click="emit('update:modelValue', false)">
        취소
      </BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.pw-form {
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
.foot-save {
  flex: 1.6;
}
.foot-cancel {
  flex: 1;
  white-space: nowrap;
}
</style>
