<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'
import UserProfileModal from '@/components/UserProfileModal.vue'
import { authApi } from '@/api/auth'
import { useToastStore } from '@/stores/toast'

const emit = defineEmits(['close'])
const toast = useToastStore()

const loading = ref(true)
const followers = ref([])
const following = ref([])
const currentTab = ref('followers') // 'followers' or 'following'

const showProfile = ref(false)
const targetNickname = ref('')

function openProfile(nickname) {
  if (nickname) {
    targetNickname.value = nickname
    showProfile.value = true
  }
}

const colors = ['#3182f6', '#f04452', '#15c47e', '#f5a623', '#9b6cf6']
function avatarColor(name) {
  let h = 0
  for (const ch of name || '') h = ch.charCodeAt(0) + h
  return colors[h % colors.length]
}

onMounted(async () => {
  try {
    const { data } = await authApi.getFollows()
    followers.value = data.followers || []
    following.value = data.following || []
  } catch (e) {
    toast.show('목록을 불러오지 못했어요', 'error')
    emit('close')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <BaseModal :model-value="true" title="팔로우 / 팔로워" @update:model-value="emit('close')" sheetClass="follow-modal-sheet">
    <div class="tabs">
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'followers' }" 
        @click="currentTab = 'followers'"
      >
        팔로워 {{ followers.length }}
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'following' }" 
        @click="currentTab = 'following'"
      >
        팔로잉 {{ following.length }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      불러오는 중...
    </div>
    
    <div v-else class="list-container">
      <ul v-if="currentTab === 'followers'" class="user-list">
        <li v-for="user in followers" :key="user.nickname" class="user-item" @click="openProfile(user.nickname)">
          <BaseAvatar 
            :src="user.profile_image" 
            :text="user.nickname.charAt(0).toUpperCase()" 
            :size="40" 
            :bg="avatarColor(user.nickname)" 
          />
          <span class="u-name">{{ user.nickname }}</span>
        </li>
        <div v-if="!followers.length" class="empty">팔로워가 없습니다.</div>
      </ul>
      
      <ul v-if="currentTab === 'following'" class="user-list">
        <li v-for="user in following" :key="user.nickname" class="user-item" @click="openProfile(user.nickname)">
          <BaseAvatar 
            :src="user.profile_image" 
            :text="user.nickname.charAt(0).toUpperCase()" 
            :size="40" 
            :bg="avatarColor(user.nickname)" 
          />
          <span class="u-name">{{ user.nickname }}</span>
        </li>
        <div v-if="!following.length" class="empty">팔로우하는 유저가 없습니다.</div>
      </ul>
    </div>

    <!-- 중첩 모달(다른 사람 프로필 보기) -->
    <UserProfileModal v-if="showProfile" :nickname="targetNickname" @close="showProfile = false" />
  </BaseModal>
</template>

<style scoped>
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--space-4);
}
.tab-btn {
  flex: 1;
  background: none;
  border: none;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
}
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.loading {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
}
.list-container {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}
.user-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}
.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.user-item:hover {
  background: var(--bg-surface-hover);
}
.u-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-tertiary);
  font-size: 14px;
}
</style>

<style>
/* 모달 배경 흰색 강제 처리 */
.follow-modal-sheet {
  background-color: #ffffff !important;
  color: #1e293b !important;
}
.follow-modal-sheet .sheet-title {
  color: #0f172a !important;
}
.follow-modal-sheet .x {
  color: #64748b !important;
}
.follow-modal-sheet .x:hover {
  color: #0f172a !important;
}
.follow-modal-sheet .u-name {
  color: #0f172a !important;
}
</style>
