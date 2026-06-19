<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const tabs = computed(() => [
  { name: 'home', label: '홈', icon: '🏠' },
  { name: 'knowledge', label: '경제지식', icon: '📚' },
  { name: 'recommend', label: '추천', icon: '📈' },
  { name: auth.isAuthenticated ? 'mypage' : 'login', label: auth.isAuthenticated ? '마이' : '로그인', icon: '👤' },
])
</script>

<template>
  <nav class="tabbar">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.name"
      :to="{ name: tab.name }"
      class="tab"
      active-class="is-active"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.tabbar {
  display: none;
}
@media (max-width: 767px) {
  .tabbar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 50;
    height: calc(var(--bottom-tab-height) + env(safe-area-inset-bottom, 0px));
    padding-bottom: env(safe-area-inset-bottom, 0px);
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: rgba(14, 17, 22, 0.92);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--border-subtle);
  }
  .tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    color: var(--text-tertiary);
    font-size: 11px;
    font-weight: 600;
  }
  .tab-icon {
    font-size: 18px;
    opacity: 0.7;
  }
  .tab.is-active {
    color: var(--accent);
  }
  .tab.is-active .tab-icon {
    opacity: 1;
  }
}
</style>
