<script setup>
import { ref, computed } from 'vue'
import BaseModal from '@/components/common/BaseModal.vue'

const props = defineProps({
  // [{ date, count, term_name, term_explanation, is_correct, user_choice, answer, question, options, explanation }]
  daily: { type: Array, default: () => [] },
})

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
const now = new Date()
const viewYear = ref(now.getFullYear())
const viewMonth = ref(now.getMonth()) // 0-11

const solvedSet = computed(() => new Set(props.daily.map((d) => d.date)))
const detailByDate = computed(() => new Map(props.daily.map((d) => [d.date, d])))

// hover: 해당 날짜에 공부한 용어명 + 설명을 작은 팝업 카드로 보여준다
const hoverDetail = ref(null)
const hoverPos = ref({ top: 0, left: 0 })
const HOVER_WIDTH = 300

function onCellEnter(d, event) {
  const detail = detailOf(d)
  if (!detail) return
  hoverDetail.value = detail
  const rect = event.currentTarget.getBoundingClientRect()
  const left = Math.min(Math.max(rect.left, 8), window.innerWidth - HOVER_WIDTH - 8)
  // 아래 공간이 부족하면 셀 위쪽에 띄운다
  const below = rect.bottom + 8
  const top = below > window.innerHeight - 160 ? rect.top - 8 - 160 : below
  hoverPos.value = { top, left }
}
function onCellLeave() {
  hoverDetail.value = null
}

// 클릭한 날짜의 풀이 상세(문제/보기/내 답·정답/해설)를 팝업으로 보여준다
const showDetail = ref(false)
const selectedDetail = ref(null)

function detailOf(d) {
  return d ? detailByDate.value.get(dateStr(viewYear.value, viewMonth.value, d)) : null
}
function openDetail(d) {
  const detail = detailOf(d)
  if (!detail) return
  hoverDetail.value = null
  selectedDetail.value = detail
  showDetail.value = true
}

// 튜터 퀴즈 화면과 동일하게 보기 상태(정답/내가 고른 오답)를 표시한다
function optionState(opt, detail) {
  if (!detail) return ''
  if (opt === detail.answer) return 'correct'
  if (opt === detail.user_choice) return 'wrong'
  return ''
}

function pad(n) {
  return n < 10 ? `0${n}` : `${n}`
}
function dateStr(y, m, d) {
  return `${y}-${pad(m + 1)}-${pad(d)}`
}

// 달력 셀: 앞쪽 빈칸 + 1~말일
const cells = computed(() => {
  const firstWeekday = new Date(viewYear.value, viewMonth.value, 1).getDay()
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const arr = []
  for (let i = 0; i < firstWeekday; i++) arr.push(null)
  for (let d = 1; d <= daysInMonth; d++) arr.push(d)
  return arr
})

const monthLabel = computed(() => `${viewYear.value}년 ${viewMonth.value + 1}월`)

const solvedThisMonth = computed(
  () => cells.value.filter((d) => d && solvedSet.value.has(dateStr(viewYear.value, viewMonth.value, d))).length,
)

function isSolved(d) {
  return d && solvedSet.value.has(dateStr(viewYear.value, viewMonth.value, d))
}
function isToday(d) {
  return d && viewYear.value === now.getFullYear() && viewMonth.value === now.getMonth() && d === now.getDate()
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value -= 1
  } else {
    viewMonth.value -= 1
  }
}
function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value += 1
  } else {
    viewMonth.value += 1
  }
}
</script>

<template>
  <div class="calendar">
    <div class="cal-head">
      <button class="nav" type="button" aria-label="이전 달" @click="prevMonth">‹</button>
      <span class="month">{{ monthLabel }}</span>
      <button class="nav" type="button" aria-label="다음 달" @click="nextMonth">›</button>
    </div>
    <p class="cal-sub">이번 달 <strong class="num">{{ solvedThisMonth }}</strong>일 풀이</p>

    <div class="grid weekdays">
      <span v-for="(w, i) in WEEKDAYS" :key="w" class="wd" :class="{ sun: i === 0, sat: i === 6 }">{{ w }}</span>
    </div>
    <div class="grid days">
      <div
        v-for="(d, i) in cells"
        :key="i"
        class="cell"
        :class="{ empty: !d, solved: isSolved(d), today: isToday(d), clickable: isSolved(d) }"
        @mouseenter="isSolved(d) && onCellEnter(d, $event)"
        @mouseleave="onCellLeave"
        @click="isSolved(d) && openDetail(d)"
      >
        <span v-if="d" class="day-num">{{ d }}</span>
        <span v-if="isSolved(d)" class="check">✓</span>
      </div>
    </div>

    <!-- hover: 용어명 + 설명 -->
    <Teleport to="body">
      <div
        v-if="hoverDetail"
        class="hover-card"
        :style="{ top: `${hoverPos.top}px`, left: `${hoverPos.left}px`, width: `${HOVER_WIDTH}px` }"
      >
        <h4 class="hc-term">{{ hoverDetail.term_name || '용어 정보 없음' }}</h4>
        <p class="hc-explain">{{ hoverDetail.term_explanation || '용어 설명이 없어요.' }}</p>
      </div>
    </Teleport>

    <!-- click: 그날 푼 문제/보기/내 답·정답·해설 (튜터 퀴즈 화면 형태) -->
    <BaseModal v-if="showDetail" v-model="showDetail" :title="selectedDetail?.date || ''">
      <div v-if="selectedDetail" class="review">
        <h3 class="rv-q">{{ selectedDetail.question }}</h3>

        <ul class="rv-options">
          <li v-for="(opt, i) in selectedDetail.options || []" :key="i">
            <div class="rv-option" :class="optionState(opt, selectedDetail)">
              <span class="rv-no">{{ i + 1 }}</span>
              <span class="rv-text">{{ opt }}</span>
            </div>
          </li>
        </ul>

        <div class="rv-feedback" :class="selectedDetail.is_correct ? 'ok' : 'no'">
          <p class="rv-title">{{ selectedDetail.is_correct ? '정답이에요! 🎉' : '아쉬워요 😅' }}</p>
          <p class="rv-answer">정답: {{ selectedDetail.answer }}</p>
          <p class="rv-explain">{{ selectedDetail.explanation }}</p>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.cal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.month {
  font-size: 22px;
  font-weight: 800;
}
.nav {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 700;
}
.nav:hover {
  color: var(--accent);
  border-color: var(--accent);
}
.cal-sub {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-3);
}
.cal-sub strong {
  color: var(--accent);
}
.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}
.weekdays {
  margin-bottom: 4px;
}
.wd {
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-tertiary);
  padding: 4px 0;
}
.wd.sun {
  color: var(--danger);
}
.wd.sat {
  color: var(--accent);
}
.cell {
  position: relative;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
}
.cell.empty {
  background: transparent;
}
.day-num {
  font-size: 19px;
  font-weight: 600;
  color: var(--text-secondary);
}
.cell.solved {
  background: rgba(21, 196, 126, 0.16);
}
.cell.solved .day-num {
  color: var(--success);
  font-weight: 700;
}
.cell.clickable {
  cursor: pointer;
}
.cell.clickable:hover {
  background: var(--success);
}
.cell.clickable:hover .day-num,
.cell.clickable:hover .check {
  color: #fff;
}
.cell.today {
  outline: 1.5px solid var(--success);
}
.check {
  position: absolute;
  bottom: 2px;
  right: 4px;
  font-size: 18px;
  font-weight: 800;
  color: var(--success);
}

/* hover 용어 카드 */
.hover-card {
  position: fixed;
  z-index: 120;
  pointer-events: none;
  padding: var(--space-4);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-elevated);
}
.hc-term {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 6px;
}
.hc-explain {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-line;
}

/* click 복습 팝업 (튜터 퀴즈 화면 형태) */
.review {
  display: flex;
  flex-direction: column;
}
.rv-q {
  font-size: 17px;
  font-weight: 800;
  line-height: 1.5;
  margin-bottom: var(--space-4);
}
.rv-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.rv-option {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1.5px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 14px;
}
.rv-no {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-pill);
  background: var(--bg-elevated);
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
}
.rv-option.correct {
  border-color: var(--success);
  background: rgba(21, 196, 126, 0.12);
}
.rv-option.wrong {
  border-color: var(--danger);
  background: var(--danger-soft);
}
.rv-feedback {
  margin-top: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1.5px solid var(--border-subtle);
  background: var(--bg-surface);
}
.rv-feedback.ok {
  border-color: var(--success);
}
.rv-feedback.no {
  border-color: var(--danger);
}
.rv-title {
  font-size: 16px;
  font-weight: 800;
}
.rv-answer {
  margin-top: 10px;
  font-weight: 700;
  color: var(--accent);
}
.rv-explain {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-line;
}
</style>
