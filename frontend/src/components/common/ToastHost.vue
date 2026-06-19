<script setup>
import { useToastStore } from '@/stores/toast'
const toast = useToastStore()
</script>

<template>
  <Teleport to="body">
    <div class="toast-host">
      <transition-group name="toast">
        <div v-for="t in toast.toasts" :key="t.id" class="toast" :class="`toast--${t.type}`">
          {{ t.message }}
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-host {
  position: fixed;
  left: 50%;
  bottom: 88px;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  pointer-events: none;
}
.toast {
  padding: 11px 18px;
  border-radius: var(--radius-pill);
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  box-shadow: var(--shadow-elevated);
}
.toast--success {
  border-color: var(--success);
}
.toast--error {
  border-color: var(--danger);
}
.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--dur-base), transform var(--dur-base) var(--ease-out);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
