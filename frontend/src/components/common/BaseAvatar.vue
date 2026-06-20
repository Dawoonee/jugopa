<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: { type: String, default: null }, // 프로필 이미지 URL (없으면 이니셜 표시)
  text: { type: String, default: '·' }, // 이미지가 없을 때 표시할 이니셜
  size: { type: Number, default: 40 }, // px
  bg: { type: String, default: 'linear-gradient(135deg, var(--accent), #5aa0ff)' },
})

const sizeStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  fontSize: `${Math.round(props.size * 0.4)}px`,
}))
</script>

<template>
  <img v-if="src" :src="src" class="avatar-img" :style="sizeStyle" alt="프로필 사진" />
  <span v-else class="avatar-text" :style="{ ...sizeStyle, background: bg }">{{ text }}</span>
</template>

<style scoped>
.avatar-img {
  display: block;
  border-radius: var(--radius-pill);
  object-fit: cover;
}
.avatar-text {
  display: grid;
  place-items: center;
  border-radius: var(--radius-pill);
  color: #fff;
  font-weight: 800;
}
</style>
