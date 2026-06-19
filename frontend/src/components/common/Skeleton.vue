<script setup>
defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '16px' },
  radius: { type: String, default: 'var(--radius-sm)' },
})
</script>

<template>
  <span class="skeleton" :style="{ width, height, borderRadius: radius }" />
</template>

<style scoped>
.skeleton {
  display: block;
  background: linear-gradient(
    100deg,
    var(--bg-surface) 30%,
    var(--bg-hover) 50%,
    var(--bg-surface) 70%
  );
  background-size: 200% 100%;
  animation: shimmer 1.3s infinite;
}
@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
