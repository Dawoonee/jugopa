<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { newsApi } from '@/api/news'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import TagChip from '@/components/common/TagChip.vue'

const emit = defineEmits(['update:modelValue', 'updated'])
const auth = useAuthStore()
const toast = useToastStore()

const form = ref({ nickname: '', email: '' })
const sectors = ref([])
const selected = ref(new Set())
const saving = ref(false)

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
  <BaseModal :model-value="true" title="회원 정보 수정" @update:model-value="emit('update:modelValue', false)">
    <div class="edit-form">
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
    </div>
    <template #footer>
      <BaseButton variant="ghost" @click="emit('update:modelValue', false)">취소</BaseButton>
      <BaseButton block :disabled="saving" @click="save">{{ saving ? '저장 중…' : '저장하기' }}</BaseButton>
    </template>
  </BaseModal>
</template>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
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
</style>
