<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseModal from '@/components/common/BaseModal.vue'

// 연속 풀이 메달 이미지
import streak3 from '@/assets/medals/streak-3.png'
import streak7 from '@/assets/medals/streak-7.png'
import streak30 from '@/assets/medals/streak-30.png'
import streak100 from '@/assets/medals/streak-100.png'
import streak200 from '@/assets/medals/streak-200.png'
// 문제풀이 갯수 메달 이미지
import count5 from '@/assets/medals/count-5.png'
import count20 from '@/assets/medals/count-20.png'
import count50 from '@/assets/medals/count-50.png'
import count100 from '@/assets/medals/count-100.png'
import count200 from '@/assets/medals/count-200.png'

const props = defineProps({
  totalSolved: { type: Number, default: 0 },
  longestStreak: { type: Number, default: 0 },
})

const auth = useAuthStore()

// 연속 풀이 퀘스트 / 문제풀이 갯수 퀘스트
const STREAK_QUESTS = [
  { threshold: 3, img: streak3 },
  { threshold: 7, img: streak7 },
  { threshold: 30, img: streak30 },
  { threshold: 100, img: streak100 },
  { threshold: 200, img: streak200 },
]
const COUNT_QUESTS = [
  { threshold: 5, img: count5 },
  { threshold: 20, img: count20 },
  { threshold: 50, img: count50 },
  { threshold: 100, img: count100 },
  { threshold: 200, img: count200 },
]

const streakMedals = computed(() =>
  STREAK_QUESTS.map(({ threshold, img }) => ({
    id: `streak-${threshold}`,
    threshold,
    img,
    label: `${threshold}일 연속`,
    condition: `${threshold}일 연속 출석`,
    unlocked: props.longestStreak >= threshold,
  })),
)
const countMedals = computed(() =>
  COUNT_QUESTS.map(({ threshold, img }) => ({
    id: `count-${threshold}`,
    threshold,
    img,
    label: `${threshold}문제`,
    condition: `누적 ${threshold}문제 풀이`,
    unlocked: props.totalSolved >= threshold,
  })),
)

const allMedals = computed(() => [...streakMedals.value, ...countMedals.value])
const collected = computed(() => allMedals.value.filter((m) => m.unlocked).length)

// ── 처음 획득 감지 + 축하 팝업 ──────────────────────────────
const seenKey = computed(() => `jugopa.seenMedals.${auth.user?.username || 'guest'}`)

function loadSeen() {
  try {
    return new Set(JSON.parse(localStorage.getItem(seenKey.value) || '[]'))
  } catch {
    return new Set()
  }
}
function saveSeen(set) {
  localStorage.setItem(seenKey.value, JSON.stringify([...set]))
}

const queue = ref([]) // 새로 획득한 메달 큐 (하나씩 순서대로)
const activeMedal = ref(null)
const modalMode = ref('congrats') // 'congrats' | 'view'
const modalOpen = ref(false)

function showNext() {
  if (!queue.value.length) {
    modalOpen.value = false
    activeMedal.value = null
    return
  }
  activeMedal.value = queue.value[0]
  modalMode.value = 'congrats'
  modalOpen.value = true
}

// unlocked 상태가 바뀔 때마다 처음 보는 메달을 큐에 적재
watch(
  () => allMedals.value.filter((m) => m.unlocked).map((m) => m.id).join(','),
  () => {
    const seen = loadSeen()
    const fresh = allMedals.value.filter((m) => m.unlocked && !seen.has(m.id) && !queue.value.some((q) => q.id === m.id))
    if (!fresh.length) return
    queue.value.push(...fresh)
    if (!modalOpen.value) showNext()
  },
  { immediate: true },
)

function onModalClose() {
  if (modalMode.value === 'congrats' && activeMedal.value) {
    const seen = loadSeen()
    seen.add(activeMedal.value.id)
    saveSeen(seen)
    queue.value.shift()
    showNext()
  } else {
    modalOpen.value = false
    activeMedal.value = null
  }
}

// 메달 클릭 → 해금: 재확인 / 미해금: 잠금 안내
function onMedalClick(medal) {
  activeMedal.value = medal
  modalMode.value = medal.unlocked ? 'view' : 'locked'
  modalOpen.value = true
}
</script>

<template>
  <div class="shelf">
    <div class="shelf-head">
      <h3 class="shelf-title">수집한 메달</h3>
      <span class="collected num">{{ collected }} / {{ allMedals.length }}</span>
    </div>

    <div class="group">
      <p class="group-label">🔥 연속 풀이</p>
      <div class="medals">
        <button
          v-for="m in streakMedals"
          :key="m.id"
          type="button"
          class="medal"
          :class="{ locked: !m.unlocked }"
          @click="onMedalClick(m)"
        >
          <span class="icon">
            <img v-if="m.unlocked" :src="m.img" :alt="m.label" class="medal-img" />
            <span v-else class="lock">🔒</span>
          </span>
          <span class="m-label">{{ m.label }}</span>
        </button>
      </div>
    </div>

    <div class="group">
      <p class="group-label">📚 문제풀이 갯수</p>
      <div class="medals">
        <button
          v-for="m in countMedals"
          :key="m.id"
          type="button"
          class="medal"
          :class="{ locked: !m.unlocked }"
          @click="onMedalClick(m)"
        >
          <span class="icon">
            <img v-if="m.unlocked" :src="m.img" :alt="m.label" class="medal-img" />
            <span v-else class="lock">🔒</span>
          </span>
          <span class="m-label">{{ m.label }}</span>
        </button>
      </div>
    </div>

    <!-- 메달 획득 / 재확인 / 잠금 팝업 -->
    <BaseModal v-if="activeMedal" v-model="modalOpen" @close="onModalClose">
      <!-- 미해금 메달 -->
      <div v-if="modalMode === 'locked'" class="medal-popup">
        <img :src="activeMedal.img" :alt="activeMedal.label" class="popup-img is-locked" />
        <h3 class="popup-title">아직 획득하지 못한 메달입니다</h3>
        <p class="popup-desc">{{ activeMedal.condition }} 시 해금됩니다.</p>
      </div>
      <!-- 해금된 메달 (획득/재확인) -->
      <div v-else class="medal-popup">
        <p v-if="modalMode === 'congrats'" class="popup-kicker">🎉 새로운 메달 획득!</p>
        <img :src="activeMedal.img" :alt="activeMedal.label" class="popup-img" />
        <h3 class="popup-title">{{ activeMedal.label }} 메달</h3>
        <p class="popup-desc">
          {{ activeMedal.condition }}<span v-if="modalMode === 'congrats'"> 달성!</span>
        </p>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
.shelf-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.shelf-title {
  font-size: 15px;
  font-weight: 700;
}
.collected {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent);
}
.group {
  margin-bottom: var(--space-4);
}
.group:last-child {
  margin-bottom: 0;
}
.group-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}
.medals {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-2);
}
.medal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--space-3) 4px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  transition:
    transform var(--dur-fast, 0.15s) var(--ease-out),
    box-shadow var(--dur-fast, 0.15s) var(--ease-out);
}
.medal:not(.locked):hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-elevated);
}
.medal.locked {
  opacity: 0.45;
}
.medal.locked:hover {
  opacity: 0.7;
  transform: translateY(-2px);
}
.icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  font-size: 24px;
}
.medal-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.lock {
  font-size: 24px;
}
.m-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-align: center;
}

/* 팝업 */
.medal-popup {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-3) 0 var(--space-2);
}
.popup-kicker {
  font-size: 14px;
  font-weight: 800;
  color: var(--accent);
  margin-bottom: var(--space-3);
}
.popup-img {
  width: 140px;
  height: 140px;
  object-fit: contain;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.25));
}
.popup-img.is-locked {
  filter: grayscale(1) brightness(0.85) drop-shadow(0 6px 16px rgba(0, 0, 0, 0.2));
  opacity: 0.7;
}
.popup-title {
  margin-top: var(--space-3);
  font-size: 20px;
  font-weight: 800;
}
.popup-desc {
  margin-top: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .icon {
    width: 38px;
    height: 38px;
    font-size: 20px;
  }
  .lock {
    font-size: 20px;
  }
  .m-label {
    font-size: 10px;
  }
}
</style>
