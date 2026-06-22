<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { authApi } from '@/api/auth'
import { newsApi } from '@/api/news'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'
import TagChip from '@/components/common/TagChip.vue'
import PasswordChangeModal from '@/components/PasswordChangeModal.vue'

const MAX_IMAGE_BYTES = 5 * 1024 * 1024 // 5MB

const emit = defineEmits(['update:modelValue', 'updated'])
const auth = useAuthStore()
const toast = useToastStore()

const form = ref({ nickname: '', email: '' })
const sectors = ref([])
const selected = ref(new Set())
const saving = ref(false)
const showPwModal = ref(false)

const fileInput = ref(null)
const imageFile = ref(null) // 새로 선택한 파일
const previewUrl = ref(null) // 선택 파일 미리보기 (createObjectURL)
const removeImage = ref(false) // 사진 삭제 플래그

const initial = computed(
  () => (auth.user?.nickname || auth.user?.username || '·').charAt(0).toUpperCase(),
)
// 미리보기 > 삭제 예정(없음) > 기존 이미지
const avatarSrc = computed(() => {
  if (previewUrl.value) return previewUrl.value
  if (removeImage.value) return null
  return auth.user?.profile_image || null
})

onMounted(async () => {
  const u = auth.user
  form.value = { nickname: u?.nickname || '', email: u?.email || '' }
  selected.value = new Set(u?.interest_sectors || [])
  try {
    const { data } = await newsApi.sectors()
    sectors.value = data
  } catch (e) {
    sectors.value = []
  }
})

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

function pickImage() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    toast.show('이미지 파일만 올릴 수 있어요', 'error')
    return
  }
  if (file.size > MAX_IMAGE_BYTES) {
    toast.show('5MB 이하 이미지만 올릴 수 있어요', 'error')
    return
  }
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  imageFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  removeImage.value = false
}

function clearImage() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  imageFile.value = null
  previewUrl.value = null
  removeImage.value = true
}

function toggle(id) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
  selected.value = new Set(selected.value)
}

async function save() {
  saving.value = true
  try {
    await authApi.updateProfile({
      nickname: form.value.nickname,
      email: form.value.email,
      interest_sectors: [...selected.value],
    })
    if (imageFile.value) {
      await authApi.updateProfileImage(imageFile.value)
    } else if (removeImage.value) {
      await authApi.updateProfile({ profile_image: null })
    }
    await auth.fetchProfile()
    emit('updated')
  } catch (e) {
    toast.show('수정에 실패했어요', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <BaseModal :model-value="true" title="회원 정보 수정" @update:model-value="emit('update:modelValue', false)" sheetClass="profile-edit-sheet">
    <div class="edit-form">
      <div class="avatar-edit">
        <BaseAvatar :src="avatarSrc" :text="initial" :size="88" />
        <div class="avatar-actions">
          <BaseButton variant="outline" @click="pickImage">사진 변경</BaseButton>
          <BaseButton v-if="avatarSrc" variant="ghost" @click="clearImage">사진 삭제</BaseButton>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="file-input"
          @change="onFileChange"
        />
      </div>
      <BaseInput v-model="form.nickname" label="닉네임" />
      <BaseInput v-model="form.email" label="이메일" type="email" />
      <div>
        <span class="label">관심 업종</span>
        <div class="grid">
          <button v-for="s in sectors" :key="s.id" type="button" class="pick" @click="toggle(s.id)">
            <TagChip :label="s.name" :active="selected.has(s.id)" clickable />
          </button>
        </div>
      </div>
      <BaseButton variant="outline" block @click="showPwModal = true">비밀번호 변경하기</BaseButton>
    </div>
    <template #footer>
      <BaseButton class="foot-save" :disabled="saving" @click="save">
        {{ saving ? '저장 중…' : '저장하기' }}
      </BaseButton>
      <BaseButton class="foot-cancel" variant="ghost" @click="emit('update:modelValue', false)">
        취소
      </BaseButton>
    </template>
  </BaseModal>
  <PasswordChangeModal v-if="showPwModal" v-model="showPwModal" />
</template>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.avatar-edit {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}
.avatar-actions {
  display: flex;
  gap: 8px;
}
.file-input {
  display: none;
}
.label {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.pick {
  background: none;
  border: none;
  padding: 0;
}
.foot-save {
  flex: 1.6;
}
.foot-cancel {
  flex: 1;
  white-space: nowrap;
}
</style>

<style>
/* 모달 배경 흰색 강제 처리 */
.profile-edit-sheet {
  background-color: #ffffff !important;
  color: #1e293b !important;
}
.profile-edit-sheet .sheet-title {
  color: #0f172a !important;
}
.profile-edit-sheet .x {
  color: #64748b !important;
}
.profile-edit-sheet .x:hover {
  color: #0f172a !important;
}
.profile-edit-sheet .label {
  color: #475569 !important;
}
</style>
