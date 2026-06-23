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
        <img src="@/assets/logo.png" alt="주고파 로고" class="logo-img" />
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
        <template v-if="auth.isAuthenticated">
          <button
            class="mypage-btn"
            type="button"
            aria-label="마이페이지"
            @click="goAuth"
          >
            <BaseAvatar
              :src="auth.user?.profile_image"
              :text="initial"
              :size="30"
            />
            <span class="mypage-label">마이페이지</span>
          </button>
          <button class="logout" type="button" @click="onLogout">로그아웃</button>
        </template>
        <template v-else>
          <button class="auth-btn signup-btn" type="button" @click="router.push({ name: 'signup' })">회원가입</button>
          <button class="auth-btn login-btn" type="button" @click="goAuth">로그인</button>
        </template>
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
  background: #ffffff;
  color: #1a1a1a;
  --text-primary: #1a1a1a;
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
.logo-img {
  height: 38px;
  width: auto;
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
.mypage-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 14px 0 5px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-weight: 700;
  font-size: 14px;
  transition: border-color var(--dur-fast), background var(--dur-fast), color var(--dur-fast);
}
.mypage-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}
.mypage-label {
  white-space: nowrap;
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
.auth-btn {
  height: 38px;
  padding: 0 16px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.login-btn {
  background: var(--accent);
  color: #fff;
  border: none;
}
.login-btn:hover {
  background: var(--accent-strong);
}
.signup-btn {
  background: transparent;
  color: #1a1a1a;
  border: 1px solid rgba(0, 0, 0, 0.15);
}
.signup-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}
/* 모바일: GNB는 하단 탭바로 대체 → 헤더는 로고 + 아바타만 */
@media (max-width: 767px) {
  .gnb {
    display: none;
  }
}
</style>
