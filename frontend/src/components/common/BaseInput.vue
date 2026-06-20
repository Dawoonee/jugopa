<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
})
defineEmits(['update:modelValue'])

const show = ref(false)
const isPassword = computed(() => props.type === 'password')
// 비밀번호 필드는 '보기' 토글에 따라 text/password 전환
const inputType = computed(() => (isPassword.value ? (show.value ? 'text' : 'password') : props.type))
</script>

<template>
  <label class="field">
    <span v-if="label" class="field-label">{{ label }}</span>
    <div class="field-control">
      <input
        class="field-input"
        :class="{ 'has-toggle': isPassword }"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button
        v-if="isPassword"
        type="button"
        class="toggle"
        :aria-label="show ? '비밀번호 숨기기' : '비밀번호 보기'"
        @click="show = !show"
      >
        {{ show ? '숨기기' : '보기' }}
      </button>
    </div>
  </label>
</template>

<style scoped>
.field {
  display: block;
}
.field-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.field-control {
  position: relative;
}
.field-input {
  width: 100%;
  padding: 13px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 15px;
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast);
}
.field-input.has-toggle {
  padding-right: 60px;
}
.field-input::placeholder {
  color: var(--text-tertiary);
}
.field-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.toggle {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  padding: 6px 8px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.toggle:hover {
  color: var(--accent);
}
</style>
