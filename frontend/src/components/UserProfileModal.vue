<script setup>
import { ref, onMounted, computed } from 'vue'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import client from '@/api/client' // for profile api calls

const props = defineProps({
  nickname: { type: String, required: true },
})
const emit = defineEmits(['close'])

const auth = useAuthStore()
const toast = useToastStore()

const loading = ref(true)
const profile = ref(null)

const isMe = computed(() => {
  return auth.user?.nickname === props.nickname
})

const colors = ['#3182f6', '#f04452', '#15c47e', '#f5a623', '#9b6cf6']
function avatarColor(name) {
  let h = 0
  for (const ch of name || '') h = ch.charCodeAt(0) + h
  return colors[h % colors.length]
}

onMounted(async () => {
  try {
    const { data } = await client.get(`accounts/profile/${props.nickname}/`)
    profile.value = data
  } catch (e) {
    toast.show('프로필을 불러올 수 없어요', 'error')
    emit('close')
  } finally {
    loading.value = false
  }
})

async function toggleFollow() {
  if (!auth.isAuthenticated) {
    toast.show('로그인이 필요해요', 'error')
    return
  }
  try {
    const { data } = await client.post(`accounts/profile/${props.nickname}/follow/`)
    profile.value.is_following = data.following
    profile.value.follower_count = data.follower_count
  } catch (e) {
    toast.show('처리에 실패했어요', 'error')
  }
}
</script>

<template>
  <BaseModal :model-value="true" :title="`${props.nickname}님의 프로필`" @update:model-value="emit('close')" sheetClass="profile-modal-sheet">
    <div v-if="loading" class="loading-state">
      <p>프로필을 불러오는 중...</p>
    </div>
    <div v-else-if="profile" class="profile-content">
      <div class="top-section">
        <BaseAvatar
          :src="profile.profile_image"
          :text="profile.nickname.charAt(0).toUpperCase()"
          :size="64"
          :bg="avatarColor(profile.nickname)"
        />
        <div class="info-section">
          <h2 class="nickname">{{ profile.nickname }}</h2>
          <div class="stats">
            <span>팔로워 <strong>{{ profile.follower_count }}</strong></span>
            <span>팔로잉 <strong>{{ profile.following_count }}</strong></span>
          </div>
        </div>
      </div>

      <div v-if="!isMe" class="action-section">
        <BaseButton
          block
          :variant="profile.is_following ? 'outline' : 'primary'"
          @click="toggleFollow"
        >
          {{ profile.is_following ? '언팔로우' : '팔로우' }}
        </BaseButton>
      </div>

      <div class="details-section">
        <h4 class="section-title">관심 업종</h4>
        <div v-if="profile.interest_sectors.length" class="badges">
          <span v-for="sector in profile.interest_sectors" :key="sector.id" class="badge">
            {{ sector.sector_name }}
          </span>
        </div>
        <p v-else class="muted-text">등록된 관심 업종이 없어요.</p>

        <h4 class="section-title mt-4">관심 종목</h4>
        <div v-if="profile.interest_stocks.length" class="badges">
          <span v-for="stock in profile.interest_stocks" :key="stock.stock_code" class="badge">
            {{ stock.stock_name }}
          </span>
        </div>
        <p v-else class="muted-text">등록된 관심 종목이 없어요.</p>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped>
.loading-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}
.profile-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.top-section {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.info-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nickname {
  font-size: 18px;
  font-weight: 800;
  margin: 0;
}
.stats {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}
.stats strong {
  color: var(--text-primary);
  font-weight: 700;
}
.action-section {
  margin-top: -8px;
}
.details-section {
  border-top: 1px solid var(--border-subtle);
  padding-top: var(--space-4);
}
.section-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-secondary);
}
.mt-4 {
  margin-top: 16px;
}
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.badge {
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.muted-text {
  font-size: 13px;
  color: var(--text-tertiary);
}
</style>

<style>
/* 전역 스코프: 프로필 모달 배경색을 강제로 흰색으로 설정 */
.profile-modal-sheet {
  background-color: #ffffff !important;
  color: #1e293b !important;
}
.profile-modal-sheet .sheet-title {
  color: #0f172a !important;
}
.profile-modal-sheet .x {
  color: #64748b !important;
}
.profile-modal-sheet .x:hover {
  color: #0f172a !important;
}
.profile-modal-sheet .nickname {
  color: #0f172a !important;
}
.profile-modal-sheet .stats {
  color: #475569 !important;
}
.profile-modal-sheet .stats strong {
  color: #0f172a !important;
}
.profile-modal-sheet .section-title {
  color: #475569 !important;
}
.profile-modal-sheet .badge {
  background-color: #f1f5f9 !important;
  border-color: #cbd5e1 !important;
  color: #1e293b !important;
}
.profile-modal-sheet .muted-text {
  color: #94a3b8 !important;
}
.profile-modal-sheet .btn--primary {
  color: #ffffff !important;
  background-color: #10b981 !important;
}
.profile-modal-sheet .btn--outline {
  color: #10b981 !important;
  border-color: #10b981 !important;
}
.profile-modal-sheet .btn--outline:hover {
  background-color: rgba(16, 185, 129, 0.1) !important;
}
</style>
