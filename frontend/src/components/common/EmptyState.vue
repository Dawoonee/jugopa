<script setup>
defineProps({
  icon: { type: String, default: '🗂️' },
  title: { type: String, default: '데이터가 없어요' },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="empty">
    <div class="empty-icon">{{ icon }}</div>
    <p class="empty-title">{{ title }}</p>
    <p v-if="description" class="empty-desc">{{ description }}</p>
    <slot />
  </div>
</template>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: var(--space-7) var(--space-4);
  text-align: center;
}
.empty-icon {
  font-size: 40px;
  opacity: 0.8;
}
.empty-title {
  font-weight: 700;
  color: var(--text-primary);
}
.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
