<script setup>
defineProps({
  label: { type: String, required: true },
  active: { type: Boolean, default: false },
  clickable: { type: Boolean, default: false },
})
</script>

<template>
  <span class="chip" :class="{ 'is-active': active, 'is-clickable': clickable }">
    <slot name="icon" />
    {{ label }}
  </span>
</template>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--radius-pill);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  transition: all var(--dur-fast);
}
.chip.is-clickable {
  cursor: pointer;
}
.chip.is-clickable:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
}
.chip.is-active {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}
</style>
