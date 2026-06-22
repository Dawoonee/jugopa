<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { questions, animalMap } from '@/constants/animals'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const currentStep = ref(0)
const answers = ref([])
const saving = ref(false)
const resultType = ref(null)

const currentQuestion = computed(() => questions[currentStep.value])
const resultData = computed(() => {
  if (!resultType.value) return null
  return animalMap[resultType.value]
})

function selectOption(value) {
  answers.value.push(value)
  if (currentStep.value < questions.length - 1) {
    currentStep.value++
  } else {
    finishTest()
  }
}

async function finishTest() {
  const code = answers.value.join('')
  resultType.value = code
  saving.value = true

  try {
    await authApi.updateProfile({ investment_type: code })
    await auth.fetchProfile()
    toast.show('생존 동물 테스트 완료!', 'success')
  } catch (error) {
    toast.show('결과 저장에 실패했습니다.', 'error')
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.back()
}

function getImageUrl(code) {
  return new URL(`../assets/animal/${code}.png`, import.meta.url).href
}
</script>

<template>
  <div class="page test-page">
    <div class="test-bg"></div>
    <div class="test-header">
      <button class="back-btn" @click="goBack" aria-label="뒤로가기">‹</button>
      <h2 class="page-title">야생의 주식장, 나의 생존 동물은?</h2>
      <div class="header-spacer"></div>
    </div>

    <div class="test-container card">
      <!-- 퀴즈 진행 중 -->
      <div v-if="!resultType" class="quiz-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${((currentStep) / questions.length) * 100}%` }"></div>
        </div>
        <div class="question-header">
          <span class="step-badge">Q{{ currentStep + 1 }}. {{ currentQuestion.title }}</span>
          <h3 class="question-title">{{ currentQuestion.question }}</h3>
        </div>
        <div class="options">
          <button 
            v-for="(opt, idx) in currentQuestion.options" 
            :key="idx"
            class="option-btn"
            @click="selectOption(opt.value)"
          >
            {{ opt.text }}
          </button>
        </div>
      </div>

      <!-- 결과 화면 -->
      <div v-else class="result-section">
        <h3 class="result-title">당신의 생존 동물은 <strong>{{ resultData.name }}</strong>!</h3>
        <div class="image-wrapper">
          <img :src="getImageUrl(resultType)" :alt="resultData.name" class="animal-img" />
        </div>
        <p class="result-desc">{{ resultData.desc }}</p>
        <BaseButton block @click="goBack">확인</BaseButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.test-bg {
  position: fixed;
  inset: 0;
  background-image: url('@/assets/backgrounds/test_page.png');
  background-size: cover;
  background-position: center;
  z-index: -1;
}
.test-page {
  min-height: 100vh;
  padding-bottom: var(--space-6);
}
.test-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) 0;
  margin-bottom: var(--space-4);
}
.back-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: var(--text-primary);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
.page-title {
  font-size: 18px;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary);
}
.header-spacer {
  width: 32px;
}
.test-container {
  background-color: #ffffff;
  padding: var(--space-6) var(--space-5);
  border-radius: var(--radius-xl);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 400px;
  justify-content: center;
}

/* 퀴즈 섹션 */
.quiz-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background-color: var(--primary);
  transition: width 0.3s ease;
}
.question-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  text-align: center;
}
.step-badge {
  background-color: #f0fdf4;
  color: #047857;
  font-size: 14px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 20px;
}
.question-title {
  font-size: 22px;
  font-weight: 800;
  color: #000000;
  line-height: 1.4;
  margin: 0;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.option-btn {
  background-color: #ffffff;
  border: 2px solid #e2e8f0;
  border-radius: var(--radius-lg);
  padding: 18px;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #000000;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.5;
}
.option-btn:hover {
  border-color: #10b981;
  background-color: #f0fdf4;
  color: #047857;
}

/* 결과 섹션 */
.result-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 24px;
  animation: fadeIn 0.5s ease;
}
.result-title {
  font-size: 24px;
  margin: 0;
  color: #000000;
  font-weight: 800;
}
.result-title strong {
  color: #10b981;
  font-size: 30px;
}
.image-wrapper {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.animal-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.result-desc {
  font-size: 16px;
  color: #000000;
  font-weight: 500;
  line-height: 1.6;
  background: #f8fafc;
  padding: 20px;
  border-radius: var(--radius-lg);
  margin: 0 0 10px 0;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
