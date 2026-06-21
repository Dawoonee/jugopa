<script setup>
import { onMounted } from 'vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import ToastHost from '@/components/common/ToastHost.vue'
import ChatbotWidget from '@/components/ChatbotWidget.vue'
import LoginModal from '@/components/LoginModal.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(() => {
  // 토큰이 있으면 프로필 미리 로드 (새로고침 시 로그인 유지)
  if (auth.isAuthenticated) auth.fetchProfile().catch(() => auth.logout())
})
</script>

<template>
  <DefaultLayout>
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </DefaultLayout>
  <ToastHost />
  <ChatbotWidget />
  <LoginModal v-if="auth.showLoginModal" />
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition:
    opacity var(--dur-base) var(--ease-out),
    transform var(--dur-base) var(--ease-out);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
