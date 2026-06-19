<script setup>
defineProps({
  variant: { type: String, default: 'primary' }, // primary | outline | destructive | ghost
  type: { type: String, default: 'button' },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
})
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    class="btn"
    :class="[`btn--${variant}`, { 'btn--block': block }]"
  >
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  font-size: 15px;
  font-weight: 700;
  transition:
    transform var(--dur-fast) var(--ease-out),
    background var(--dur-fast),
    border-color var(--dur-fast),
    opacity var(--dur-fast);
}
.btn:active:not(:disabled) {
  transform: scale(0.97);
}
.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.btn--block {
  width: 100%;
}
.btn--primary {
  background: var(--accent);
  color: var(--text-on-accent);
}
.btn--primary:hover:not(:disabled) {
  background: var(--accent-strong);
}
.btn--outline {
  background: transparent;
  border-color: var(--border-strong);
  color: var(--text-primary);
}
.btn--outline:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.btn--destructive {
  background: var(--danger);
  color: #fff;
}
.btn--destructive:hover:not(:disabled) {
  filter: brightness(1.08);
}
.btn--ghost {
  background: transparent;
  color: var(--text-secondary);
}
.btn--ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
