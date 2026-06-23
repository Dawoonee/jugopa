<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import cinematicVideo from '@/assets/landingpage/cinematic.mp4'

const router = useRouter()
const showWarning = ref(false)

const agreeAndEnter = () => {
  localStorage.setItem('agreedToTerms', 'true')
  router.push({ name: 'home' })
}

const handleVideoEnded = () => {
  showWarning.value = true
}
</script>

<template>
  <div class="landing-page">
    <!-- 풀스크린 배경 영상 -->
    <video 
      class="fullscreen-video" 
      :src="cinematicVideo" 
      autoplay 
      muted 
      playsinline 
      @ended="handleVideoEnded"
    ></video>

    <transition name="fade-delay">
      <div v-if="showWarning" class="modal-overlay">
        <div class="warning-modal">
          <h2>⚠️ 투자 위험 고지 ⚠️</h2>
          <p>
            본 사파리(서비스)에서 제공하는 정보는 <strong>투자 참고용</strong>입니다.<br/>
            투자의 최종 결정은 본인의 판단에 따라 이루어져야 하며,<br/>
            투자 결과에 따른 <strong>원금 손실의 위험</strong>이 있습니다.
          </p>
          <p class="question">위 내용에 동의하고 입장하시겠습니까?</p>
          <BaseButton @click="agreeAndEnter" class="agree-btn" block>동의하고 입장하기</BaseButton>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.landing-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #000; /* 영상을 로드하는 동안 검은 배경 */
  z-index: 9999;
}

.fullscreen-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  backdrop-filter: blur(4px);
}

.warning-modal {
  background: var(--bg-surface, #161b22);
  color: var(--text-primary, #ffffff);
  padding: clamp(30px, 5vw, 60px) clamp(20px, 4vw, 40px);
  border-radius: var(--radius-xl, 24px);
  text-align: center;
  max-width: 750px;
  width: 92%;
  border: 4px solid var(--danger, #f04452);
  box-shadow: 0 20px 50px rgba(240, 68, 82, 0.4);
}

.warning-modal h2 {
  color: var(--danger, #f04452);
  margin-bottom: clamp(20px, 4vw, 30px);
  font-size: clamp(26px, 6vw, 40px);
  font-weight: 900;
  word-break: keep-all;
}

.warning-modal p {
  line-height: 1.8;
  margin-bottom: clamp(20px, 4vw, 30px);
  color: var(--text-secondary, #9aa5b1);
  font-size: clamp(17px, 4vw, 24px);
  word-break: keep-all;
}

.warning-modal strong {
  color: var(--danger, #f04452);
}

.question {
  font-weight: 900;
  color: var(--text-primary, #ffffff) !important;
  margin-bottom: clamp(24px, 5vw, 40px) !important;
  font-size: clamp(19px, 4.5vw, 28px) !important;
}

.agree-btn {
  background: var(--danger, #f04452) !important;
  color: #ffffff !important;
  border-color: var(--danger, #f04452) !important;
  font-size: clamp(18px, 4vw, 24px);
  font-weight: 800;
  padding: clamp(14px, 3vw, 20px);
  border-radius: 12px;
}
.agree-btn:hover {
  filter: brightness(1.1);
}

.fade-delay-enter-active {
  transition: opacity 0.5s ease;
}
.fade-delay-enter-from {
  opacity: 0;
}
</style>
