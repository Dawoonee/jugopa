<script setup>
import { ref, onMounted } from 'vue'
import { tutorsApi } from '@/api/tutors'
import BaseButton from '@/components/common/BaseButton.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import bgQuiz from '@/assets/backgrounds/quiz.png'

const quiz = ref(null)
const loading = ref(true)
const selected = ref(null)
const result = ref(null) // { is_correct, answer, explanation }
const submitting = ref(false)

onMounted(async () => {
  try {
    // '오늘의 용어'와 동일한 주제의 퀴즈를 서버에서 받아온다
    const { data } = await tutorsApi.todayQuiz()
    quiz.value = data
    // 오늘 이미 풀었다면 복습(read-only) 모드로 전환한다
    if (data.solved_today && data.result) {
      applyResult(data.result)
    }
  } catch (e) {
    quiz.value = null
  } finally {
    loading.value = false
  }
})

// 채점 결과를 화면 상태에 반영한다 (제출 직후/복습/중복제출 공통)
function applyResult(data) {
  selected.value = data.user_choice ?? selected.value
  result.value = {
    is_correct: data.is_correct,
    answer: data.answer,
    explanation: data.explanation,
  }
}

async function submit() {
  if (selected.value === null || result.value) return
  submitting.value = true
  try {
    const { data } = await tutorsApi.checkQuiz(quiz.value.id, selected.value)
    applyResult(data)
  } catch (e) {
    // 이미 오늘 푼 경우(409): 기존 결과로 복습 화면 전환
    if (e?.response?.status === 409) {
      applyResult(e.response.data)
    }
  } finally {
    submitting.value = false
  }
}

function optionState(opt) {
  if (!result.value) return selected.value === opt ? 'selected' : ''
  if (opt === result.value.answer) return 'correct'
  if (opt === selected.value) return 'wrong'
  return ''
}
</script>

<template>
  <div class="page quiz theme-light">
    <div class="weather-bg" :style="{ backgroundImage: `url(${bgQuiz})`, transform: 'scale(1.02)' }"></div>
    <RouterLink :to="{ name: 'knowledge' }" class="back-link">‹ 경제 용어 다시 보기</RouterLink>

    <div v-if="loading" class="card">
      <Skeleton height="22px" width="40%" />
      <div style="height: 16px" />
      <Skeleton v-for="n in 4" :key="n" height="52px" radius="var(--radius-md)" />
    </div>

    <EmptyState v-else-if="!quiz" title="퀴즈가 없어요" description="잠시 후 다시 시도해 주세요" />

    <template v-else>
      <span class="eyebrow">오늘의 퀴즈</span>
      <h1 class="quiz-q">{{ quiz.question }}</h1>

      <ul class="options">
        <li v-for="(opt, i) in quiz.options" :key="i">
          <button
            type="button"
            class="option"
            :class="optionState(opt)"
            :disabled="!!result"
            @click="selected = opt"
          >
            <span class="option-no">{{ i + 1 }}</span>
            <span class="option-text">{{ opt }}</span>
          </button>
        </li>
      </ul>

      <transition name="fade">
        <div v-if="result" class="feedback card" :class="result.is_correct ? 'ok' : 'no'">
          <p class="feedback-title">{{ result.is_correct ? '정답이에요! 🎉' : '아쉬워요 😅' }}</p>
          <p class="feedback-answer">정답: {{ result.answer }}</p>
          <p class="feedback-explain">{{ result.explanation }}</p>
        </div>
      </transition>

      <BaseButton
        v-if="!result"
        block
        class="submit"
        :disabled="selected === null || submitting"
        @click="submit"
      >
        {{ submitting ? '채점 중…' : '제출하기' }}
      </BaseButton>
      <BaseButton v-else variant="secondary" block class="submit" @click="$router.push({ name: 'knowledge' })">
        뒤로가기
      </BaseButton>
    </template>
  </div>
</template>

<style scoped>
.back-link {
  display: block;
  width: fit-content;
  margin-bottom: var(--space-6);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
}
.back-link:hover {
  color: var(--accent);
}
.eyebrow {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--accent);
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
}
.quiz-q {
  margin: var(--space-4) 0 var(--space-5);
  font-size: 20px;
  font-weight: 800;
  line-height: 1.5;
}
.options {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1.5px solid var(--border-subtle);
  color: var(--text-primary);
  text-align: left;
  font-size: 15px;
  transition: all var(--dur-fast);
}
.option-no {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-pill);
  background: var(--bg-elevated);
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
}
.option.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.option.selected .option-no {
  background: var(--accent);
  color: #fff;
}
.option.correct {
  border-color: var(--success);
  background: rgba(21, 196, 126, 0.12);
}
.option.wrong {
  border-color: var(--danger);
  background: var(--danger-soft);
}
.submit {
  margin-top: var(--space-5);
}
.feedback {
  margin-top: var(--space-5);
}
.feedback.ok {
  border-color: var(--success);
}
.feedback.no {
  border-color: var(--danger);
}
.feedback-title {
  font-size: 17px;
  font-weight: 800;
}
.feedback-answer {
  margin-top: 10px;
  font-weight: 700;
  color: var(--accent);
}
.feedback-explain {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.7;
}
.fade-enter-active {
  transition: opacity var(--dur-base);
}
.fade-enter-from {
  opacity: 0;
}
</style>
