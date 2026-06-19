<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  daily: { type: Array, default: () => [] }, // [{ date: 'YYYY-MM-DD', count }]
})

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
const now = new Date()
const viewYear = ref(now.getFullYear())
const viewMonth = ref(now.getMonth()) // 0-11

const solvedSet = computed(() => new Set(props.daily.map((d) => d.date)))

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
        :class="{ empty: !d, solved: isSolved(d), today: isToday(d) }"
      >
        <span v-if="d" class="day-num">{{ d }}</span>
        <span v-if="isSolved(d)" class="check">✓</span>
      </div>
    </div>
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
  font-size: 15px;
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
  font-size: 11px;
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
  font-size: 12px;
  color: var(--text-secondary);
}
.cell.solved {
  background: var(--accent-soft);
}
.cell.solved .day-num {
  color: var(--accent);
  font-weight: 700;
}
.cell.today {
  outline: 1.5px solid var(--accent);
}
.check {
  position: absolute;
  bottom: 2px;
  font-size: 10px;
  font-weight: 800;
  color: var(--accent);
}
</style>
