<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { communityApi } from '@/api/community'
import { stocksApi } from '@/api/stocks'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import CommunityPostCard from '@/components/CommunityPostCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const auth = useAuthStore()
const toast = useToastStore()
const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

const code = route.params.code
const stock = ref(null)
const posts = ref([])
const loading = ref(true)
const visible = ref(8) // 클라이언트 무한스크롤
const showWrite = ref(false)
const draft = ref({ title: '', content: '' })

const shown = computed(() => posts.value.slice(0, visible.value))

onMounted(async () => {
  try {
    const [detail, list] = await Promise.allSettled([stocksApi.detail(code), communityApi.posts(code)])
    if (detail.status === 'fulfilled') stock.value = detail.value.data
    if (list.status === 'fulfilled') posts.value = list.value.data
    await fetchWeather()
  } finally {
    loading.value = false
  }
})

function onScroll(e) {
  const el = e.target.scrollingElement || document.documentElement
  if (el.scrollTop + window.innerHeight >= el.scrollHeight - 200) {
    if (visible.value < posts.value.length) visible.value += 8
  }
}
onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

async function submitPost() {
  if (!draft.value.content.trim()) return
  try {
    const { data } = await communityApi.createPost({
      title: draft.value.title || '제목 없음',
      content: draft.value.content,
      stock: stock.value.id,
    })
    posts.value.unshift(data)
    showWrite.value = false
    draft.value = { title: '', content: '' }
    toast.show('글을 등록했어요', 'success')
  } catch (e) {
    toast.show('등록에 실패했어요', 'error')
  }
}
</script>

<template>
  <div class="page community" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <header class="comm-top">
      <RouterLink :to="{ name: 'stock-detail', params: { code } }" class="back">‹ {{ stock?.stock_name || '종목' }}</RouterLink>
      <span class="count num">{{ posts.length }}개의 글</span>
    </header>

    <BaseButton v-if="auth.isAuthenticated" block class="write-btn" @click="showWrite = true">
      ✏️ 글쓰기
    </BaseButton>

    <div v-if="loading" class="list">
      <Skeleton v-for="n in 3" :key="n" height="120px" radius="var(--radius-lg)" />
    </div>
    <EmptyState v-else-if="!posts.length" icon="💬" title="첫 글의 주인공이 되어보세요" />
    <div v-else class="list">
      <CommunityPostCard v-for="p in shown" :key="p.id" :post="p" />
    </div>

    <BaseModal v-if="showWrite" v-model="showWrite" title="글쓰기">
      <div class="write-form">
        <BaseInput v-model="draft.title" label="제목" placeholder="제목을 입력하세요" />
        <label class="field">
          <span class="field-label">내용</span>
          <textarea v-model="draft.content" class="textarea" rows="5" placeholder="내용을 입력하세요" />
        </label>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showWrite = false">취소</BaseButton>
        <BaseButton block @click="submitPost">등록</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.comm-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.back {
  color: var(--text-secondary);
  font-weight: 700;
  font-size: 15px;
}
.back:hover {
  color: var(--accent);
}
.count {
  font-size: 13px;
  color: var(--text-tertiary);
}
.write-btn {
  margin-bottom: var(--space-4);
}
.list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.write-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.field-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}
.textarea {
  width: 100%;
  padding: 13px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 15px;
  resize: vertical;
}
.textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
</style>
