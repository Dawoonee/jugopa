<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseAvatar from '@/components/common/BaseAvatar.vue'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const navItems = [
  { name: 'home', label: '홈' },
  { name: 'knowledge', label: '경제 지식' },
  { name: 'recommend', label: '주식 추천' },
]

const initial = computed(() => {
  const n = auth.user?.nickname || auth.user?.username || ''
  return n ? n.charAt(0).toUpperCase() : '·'
})

function goAuth() {
  if (auth.isAuthenticated) {
    router.push({ name: 'mypage' })
  } else {
    auth.showLoginModal = true
  }
}

function onLogout() {
  auth.logout()
  toast.show('로그아웃되었어요')
  router.push({ name: 'home' })
}
</script>

<template>
  <header class="header">
    <div class="header-inner">
      <RouterLink :to="{ name: 'home' }" class="logo">
        <span class="logo-badge">주</span>
        <span class="logo-text">주고파</span>
      </RouterLink>

      <nav class="gnb">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name }"
          class="gnb-item"
          active-class="is-active"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="user-area">
        <button
          class="avatar"
          :class="{ 'avatar--user': auth.isAuthenticated }"
          type="button"
          :aria-label="auth.isAuthenticated ? '마이페이지' : '로그인'"
          @click="goAuth"
        >
          <BaseAvatar
            v-if="auth.isAuthenticated"
            :src="auth.user?.profile_image"
            :text="initial"
            :size="38"
          />
          <template v-else>로그인</template>
        </button>
        <button v-if="auth.isAuthenticated" class="logout" type="button" @click="onLogout">로그아웃</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--header-height);
  background: rgba(14, 17, 22, 0.82);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}
.header-inner {
  max-width: var(--content-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-5);
}
.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: 800;
}
.logo-badge {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--accent), #5aa0ff);
  color: #fff;
  font-size: 15px;
}
.logo-text {
  font-size: 17px;
}
.gnb {
  display: flex;
  gap: var(--space-2);
  flex: 1;
}
.gnb-item {
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  font-weight: 600;
  transition: color var(--dur-fast), background var(--dur-fast);
}
.gnb-item:hover {
  color: var(--text-primary);
}
.gnb-item.is-active {
  color: var(--text-on-accent);
  background: var(--accent);
}
.user-area {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.avatar {
  min-width: 38px;
  height: 38px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-strong);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-weight: 700;
}
.avatar:hover {
  border-color: var(--accent);
}
.avatar--user {
  min-width: 0;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius-pill);
}
.avatar--user:hover {
  box-shadow: 0 0 0 2px var(--accent);
}
.logout {
  height: 38px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
}
.logout:hover {
  color: var(--danger);
  border-color: var(--danger);
}
/* 모바일: GNB는 하단 탭바로 대체 → 헤더는 로고 + 아바타만 */
@media (max-width: 767px) {
  .gnb {
    display: none;
  }
}
</style>
