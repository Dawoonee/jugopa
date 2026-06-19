<script setup>
import AppHeader from './AppHeader.vue'
import BottomTabBar from './BottomTabBar.vue'
</script>

<template>
  <div class="layout">
    <AppHeader />
    <main class="layout-main">
      <slot />
    </main>
    <BottomTabBar />
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.layout-main {
  flex: 1;
}
/* 모바일: 하단 탭바 높이만큼 여백 */
@media (max-width: 767px) {
  .layout-main {
    padding-bottom: calc(var(--bottom-tab-height) + env(safe-area-inset-bottom, 0px));
  }
}
</style>
