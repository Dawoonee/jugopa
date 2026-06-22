<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: true },
  title: { type: String, default: '' },
  maxWidth: { type: String, default: '440px' },
  sheetClass: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'close'])

function close() {
  emit('update:modelValue', false)
  emit('close')
}
function onKey(e) {
  if (e.key === 'Escape') close()
}
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="modelValue" class="backdrop" @click.self="close">
        <div class="sheet" :class="sheetClass" role="dialog" aria-modal="true" :style="{ '--modal-max-width': maxWidth }">
          <header v-if="title || $slots.header" class="sheet-head">
            <slot name="header">
              <h3 class="sheet-title">{{ title }}</h3>
            </slot>
            <button class="x" type="button" aria-label="닫기" @click="close">✕</button>
          </header>
          <div class="sheet-body">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="sheet-foot">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}
.sheet {
  width: 100%;
  max-width: var(--modal-max-width);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-elevated);
  overflow: hidden;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}
.sheet-body {
  padding: var(--space-3) var(--space-5) var(--space-5);
  overflow-y: auto;
}
.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-5) var(--space-3);
}
.sheet-title {
  font-size: 18px;
  font-weight: 800;
}
.x {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: 16px;
}
.x:hover {
  color: var(--text-primary);
}
.sheet-body {
  padding: var(--space-3) var(--space-5) var(--space-5);
}
.sheet-foot {
  padding: var(--space-3) var(--space-5) var(--space-5);
  display: flex;
  gap: var(--space-3);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--dur-base);
}
.modal-enter-active .sheet,
.modal-leave-active .sheet {
  transition: transform var(--dur-base) var(--ease-out);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .sheet,
.modal-leave-to .sheet {
  transform: scale(0.96);
}

/* 모바일: 바텀시트 */
@media (max-width: 767px) {
  .backdrop {
    align-items: flex-end;
    padding: 0;
  }
  .sheet {
    max-width: none;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }
  .modal-enter-from .sheet,
  .modal-leave-to .sheet {
    transform: translateY(100%);
  }
}
</style>
