<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'
import { stocksApi } from '@/api/stocks'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import ProfileEditModal from '@/components/ProfileEditModal.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAvatar from '@/components/common/BaseAvatar.vue'
import TagChip from '@/components/common/TagChip.vue'
import AchievementCalendar from '@/components/AchievementCalendar.vue'
import MedalShelf from '@/components/MedalShelf.vue'
import FollowListModal from '@/components/FollowListModal.vue'
import { useCountUp } from '@/composables/useCountUp'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

const stats = ref({ bookmark_count: 0, quiz_count: 0, today_visited: false })
const bookmarks = ref([])
const calendar = ref({ total_solved: 0, current_streak: 0, longest_streak: 0, daily: [] })
const showEdit = ref(false)
const showWithdraw = ref(false)
const showFollows = ref(false)

const user = computed(() => auth.user)
const initial = computed(() => (user.value?.nickname || user.value?.username || '·').charAt(0).toUpperCase())

const bookmarkCount = useCountUp(() => stats.value.bookmark_count)
const quizCount = useCountUp(() => stats.value.quiz_count)

onMounted(async () => {
  await auth.fetchProfile().catch(() => {})
  try {
    const [s, b, c] = await Promise.allSettled([
      authApi.getStats(),
      stocksApi.bookmarks(),
      authApi.quizCalendar(),
    ])
    if (s.status === 'fulfilled') stats.value = s.value.data
    if (b.status === 'fulfilled') bookmarks.value = b.value.data
    if (c.status === 'fulfilled') calendar.value = c.value.data
  } catch (e) {
    /* noop */
  }
  await fetchWeather()
})

async function withdraw() {
  try {
    await authApi.deleteProfile()
    auth.logout()
    toast.show('탈퇴 처리되었어요')
    router.push({ name: 'home' })
  } catch (e) {
    toast.show('탈퇴에 실패했어요', 'error')
  }
}

function onLogout() {
  auth.logout()
  toast.show('로그아웃되었어요')
  router.push({ name: 'home' })
}

function onUpdated() {
  showEdit.value = false
  toast.show('프로필을 수정했어요', 'success')
}
</script>

<template>
  <div class="page mypage" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <!-- 프로필 카드 -->
    <section class="profile card">
      <BaseAvatar :src="user?.profile_image" :text="initial" :size="64" />
      <div class="p-info">
        <h1 class="p-name">{{ user?.nickname }}</h1>
        <p class="p-email">{{ user?.email || '이메일 미등록' }}</p>
        <p class="p-id num">@{{ user?.username }}</p>
      </div>
      <BaseButton variant="outline" @click="showEdit = true">수정</BaseButton>
    </section>

    <!-- 통계 -->
    <section class="stats">
      <div class="stat card" @click="showFollows = true" style="cursor: pointer;">
        <span class="stat-num num">{{ stats.follower_count || 0 }}</span>
        <span class="stat-label">팔로워</span>
      </div>
      <div class="stat card" @click="showFollows = true" style="cursor: pointer;">
        <span class="stat-num num">{{ stats.following_count || 0 }}</span>
        <span class="stat-label">팔로잉</span>
      </div>
      <div class="stat card">
        <span class="stat-num num">{{ bookmarkCount.display.value }}</span>
        <span class="stat-label">관심 종목</span>
      </div>
    </section>

    <div class="cols">
      <!-- 정보 -->
      <section class="card info">
        <h2 class="block-title">내 정보</h2>
        <dl class="info-list">
          <div class="info-row"><dt>닉네임</dt><dd>{{ user?.nickname }}</dd></div>
          <div class="info-row"><dt>이메일</dt><dd>{{ user?.email || '-' }}</dd></div>
          <div class="info-row">
            <dt>가입일</dt>
            <dd class="num">{{ user?.created_at ? new Date(user.created_at).toLocaleDateString('ko-KR') : '-' }}</dd>
          </div>
          <div class="info-row">
            <dt>관심 업종</dt>
            <dd class="chips">
              <TagChip v-for="n in user?.interest_sector_names || []" :key="n" :label="n" active />
              <span v-if="!user?.interest_sector_names?.length" class="muted">없음</span>
            </dd>
          </div>
        </dl>
      </section>

      <!-- 관심 종목 -->
      <section class="card stocks">
        <h2 class="block-title">관심 종목</h2>
        <div v-if="bookmarks.length" class="stock-chips">
          <RouterLink
            v-for="b in bookmarks"
            :key="b.stock_code"
            :to="{ name: 'stock-detail', params: { code: b.stock_code } }"
          >
            <TagChip :label="b.stock_name" clickable />
          </RouterLink>
        </div>
        <p v-else class="muted">아직 관심 종목이 없어요</p>
      </section>
    </div>

    <!-- 성취도 -->
    <section class="card achievement">
      <div class="ach-head">
        <h2 class="block-title">성취도</h2>
        <div class="ach-stats">
          <span class="ach-stat">🔥 연속 <strong class="num">{{ calendar.current_streak }}</strong>일</span>
          <span class="ach-stat">📚 누적 <strong class="num">{{ calendar.total_solved }}</strong>문제</span>
        </div>
      </div>
      <AchievementCalendar :daily="calendar.daily" />
      <hr class="divider" />
      <MedalShelf :total-solved="calendar.total_solved" :longest-streak="calendar.longest_streak" />
    </section>

    <!-- 액션 -->
    <section class="actions">
      <BaseButton block @click="showEdit = true">회원 정보 수정</BaseButton>
      <BaseButton variant="secondary" block @click="onLogout">로그아웃</BaseButton>
      <BaseButton variant="destructive" block @click="showWithdraw = true">회원 탈퇴</BaseButton>
    </section>

    <ProfileEditModal v-if="showEdit" v-model="showEdit" @updated="onUpdated" />
    <FollowListModal v-if="showFollows" @close="showFollows = false" />

    <BaseModal v-if="showWithdraw" v-model="showWithdraw" title="">
      <div class="withdraw">
        <div class="warn">⚠️</div>
        <h3 class="w-title">정말 탈퇴하시겠어요?</h3>
        <p class="w-desc">탈퇴 시 모든 정보가 삭제되며 복구할 수 없습니다.</p>
      </div>
      <template #footer>
        <BaseButton variant="ghost" block @click="showWithdraw = false">취소</BaseButton>
        <BaseButton variant="destructive" block @click="withdraw">탈퇴하기</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.profile {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
.p-info {
  flex: 1;
}
.p-name {
  font-size: 20px;
  font-weight: 800;
}
.p-email {
  color: var(--text-secondary);
  font-size: 14px;
}
.p-id {
  color: var(--text-tertiary);
  font-size: 13px;
}
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--space-4);
}
.stat-num {
  font-size: 26px;
  font-weight: 800;
  color: var(--accent);
}
.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}
.cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
.block-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: var(--space-4);
}
.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin: 0;
}
.info-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}
.info-row dt {
  color: var(--text-tertiary);
  font-size: 14px;
}
.info-row dd {
  margin: 0;
  font-weight: 600;
  text-align: right;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}
.stock-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.muted {
  color: var(--text-tertiary);
  font-size: 14px;
}
.achievement {
  margin-bottom: var(--space-4);
}
.ach-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}
.ach-head .block-title {
  margin-bottom: 0;
  font-size: 20px;
}
.ach-stats {
  display: flex;
  gap: var(--space-3);
}
.ach-stat {
  font-size: 13px;
  color: var(--text-secondary);
}
.ach-stat strong {
  color: var(--accent);
}
.divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: var(--space-4) 0;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.withdraw {
  text-align: center;
  padding: var(--space-3) 0;
}
.warn {
  font-size: 44px;
}
.w-title {
  margin-top: var(--space-3);
  font-size: 19px;
  font-weight: 800;
}
.w-desc {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}
@media (max-width: 767px) {
  .cols {
    grid-template-columns: 1fr;
  }
}
</style>
