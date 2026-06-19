<script setup>
import { ref, onMounted } from 'vue'
import { tutorsApi } from '@/api/tutors'
import BaseButton from '@/components/common/BaseButton.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const term = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await tutorsApi.dailyTerm()
    term.value = data.term
  } catch (e) {
    term.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page knowledge">
    <span class="eyebrow">오늘의 경제 용어</span>

    <div v-if="loading" class="card">
      <Skeleton height="32px" width="50%" />
      <div style="height: 16px" />
      <Skeleton height="14px" />
      <div style="height: 8px" />
      <Skeleton height="14px" width="80%" />
    </div>

    <EmptyState v-else-if="!term" title="오늘의 용어가 없어요" description="잠시 후 다시 시도해 주세요" />

    <article v-else class="term-card card">
      <h1 class="term-name">{{ term.term_name }}</h1>
      <p class="term-explanation">{{ term.explanation }}</p>
    </article>

    <BaseButton v-if="term" block class="quiz-cta" @click="$router.push({ name: 'quiz' })">
      퀴즈 풀러 가기 →
    </BaseButton>
  </div>
</template>

<style scoped>
.eyebrow {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  margin-bottom: var(--space-4);
}
.term-name {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: var(--space-4);
}
.term-explanation {
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-line;
}
.quiz-cta {
  margin-top: var(--space-5);
}
</style>
