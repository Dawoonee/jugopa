<template>
  <div
    class="mascot-widget"
    :class="{ 'is-greeting': showGreeting }"
    @click="handleClick"
    @mouseenter="isHovering = true"
    @mouseleave="isHovering = false"
  >
    <transition name="bubble-fade">
      <div v-if="showGreeting" class="speech-bubble">
        {{ currentGreeting }}
      </div>
    </transition>

    <div class="mascot-body" :class="{ 'is-excited': isHovering || showGreeting }">
      <img
        :src="mascotImage"
        alt="주고파 마스코트"
        class="mascot-image"
        draggable="false"
      />

      <span class="eye eye-left" :class="{ blinking: isBlinking }"></span>
      <span class="eye eye-right" :class="{ blinking: isBlinking }"></span>

      <span
        v-for="sparkle in sparkles"
        :key="sparkle.id"
        class="sparkle"
        :style="sparkle.style"
      ></span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import mascotImage from '@/assets/jugopa-mascot.png'

const isBlinking = ref(false)
const isHovering = ref(false)
const showGreeting = ref(false)
const currentGreeting = ref('')

const greetings = [
  '오늘도 좋은 투자 되세요!',
  '주고파가 함께할게요',
  '상승장 가즈아!',
  '오늘의 추천 종목 확인해보세요',
]

const sparkles = [
  { id: 1, style: { top: '8%', right: '6%', animationDelay: '0s' } },
  { id: 2, style: { top: '22%', right: '-2%', animationDelay: '0.6s' } },
  { id: 3, style: { top: '2%', right: '20%', animationDelay: '1.2s' } },
]

let blinkTimer = null
let greetingTimer = null

const scheduleNextBlink = () => {
  const delay = 2400 + Math.random() * 2600
  blinkTimer = setTimeout(() => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
      scheduleNextBlink()
    }, 140)
  }, delay)
}

const handleClick = () => {
  clearTimeout(greetingTimer)
  currentGreeting.value = greetings[Math.floor(Math.random() * greetings.length)]
  showGreeting.value = true
  greetingTimer = setTimeout(() => {
    showGreeting.value = false
  }, 2200)
}

onMounted(() => {
  scheduleNextBlink()
})

onUnmounted(() => {
  clearTimeout(blinkTimer)
  clearTimeout(greetingTimer)
})
</script>

<style scoped>
.mascot-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 40;
  cursor: pointer;
  user-select: none;
}

/* 모바일: 하단 탭바 위로 올려 겹침 방지 */
@media (max-width: 767px) {
  .mascot-widget {
    bottom: calc(var(--bottom-tab-height) + env(safe-area-inset-bottom, 0px) + 12px);
  }
}

.mascot-body {
  position: relative;
  width: 96px;
  height: auto;
  animation: float 3.2s ease-in-out infinite;
  transform-origin: bottom center;
}

.mascot-body.is-excited {
  animation: float-excited 0.9s ease-in-out infinite;
}

.mascot-image {
  width: 100%;
  height: auto;
  display: block;
  pointer-events: none;
}

.eye {
  position: absolute;
  width: 9%;
  height: 9%;
  border-radius: 50%;
  background: #d3a365;
  opacity: 0;
  transform: translate(-50%, -50%) scaleY(1);
  transition: opacity 0.05s linear;
}

.eye-left {
  left: 25.7%;
  top: 24.4%;
}

.eye-right {
  left: 59.6%;
  top: 28.6%;
}

.eye.blinking {
  opacity: 1;
  animation: blink 0.14s ease-in-out;
}

.sparkle {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #fac775;
  animation: twinkle 1.8s ease-in-out infinite;
}

.speech-bubble {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 10px;
  background: var(--color-background-primary, #fff);
  border: 1px solid var(--color-border-tertiary, #e3e1d8);
  border-radius: 12px;
  padding: 8px 14px;
  font-size: 13px;
  color: #1a1a1a;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
}

.speech-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  right: 18px;
  border: 6px solid transparent;
  border-top-color: var(--color-background-primary, #fff);
}

.bubble-fade-enter-active,
.bubble-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.bubble-fade-enter-from,
.bubble-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scaleY(1);
  }
  35% {
    transform: translateY(-10px) rotate(-2deg) scaleY(1.02);
  }
  70% {
    transform: translateY(-2px) rotate(2deg) scaleY(0.99);
  }
}

@keyframes float-excited {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scaleY(1);
  }
  50% {
    transform: translateY(-14px) rotate(-3deg) scaleY(1.04);
  }
}

@keyframes blink {
  0%, 100% {
    transform: translate(-50%, -50%) scaleY(1);
  }
  50% {
    transform: translate(-50%, -50%) scaleY(0.08);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.15;
    transform: scale(0.6);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascot-body,
  .mascot-body.is-excited,
  .sparkle {
    animation: none;
  }
}
</style>
