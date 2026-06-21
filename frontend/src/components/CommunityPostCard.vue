<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { communityApi } from '@/api/community'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseAvatar from '@/components/common/BaseAvatar.vue'

const props = defineProps({
  post: { type: Object, required: true },
})

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

function goDetail() {
  router.push({
    name: 'community-post-detail',
    params: { code: props.post.stock_code, postId: props.post.id },
  })
}

const liked = ref(props.post.liked)
const likeCount = ref(props.post.like_count)
const bounce = ref(false)

const colors = ['#3182f6', '#f04452', '#15c47e', '#f5a623', '#9b6cf6']
function avatarColor(name) {
  let h = 0
  for (const ch of name || '') h = ch.charCodeAt(0) + h
  return colors[h % colors.length]
}

async function toggleLike() {
  if (!auth.isAuthenticated) {
    toast.show('로그인이 필요해요', 'error')
    return
  }
  // optimistic
  liked.value = !liked.value
  likeCount.value += liked.value ? 1 : -1
  bounce.value = true
  setTimeout(() => (bounce.value = false), 300)
  try {
    const { data } = await communityApi.toggleLike(props.post.id)
    liked.value = data.liked
    likeCount.value = data.like_count
  } catch (e) {
    liked.value = !liked.value
    likeCount.value += liked.value ? 1 : -1
  }
}
</script>

<template>
  <article class="post card">
    <div class="post-click" @click="goDetail">
      <header class="post-head">
        <BaseAvatar
          :src="post.profile_image"
          :text="(post.nickname || post.username || '?').charAt(0).toUpperCase()"
          :size="36"
          :bg="avatarColor(post.username)"
        />
        <div class="meta">
          <span class="name">{{ post.nickname || post.username }}</span>
          <span class="date">{{ new Date(post.created_at).toLocaleDateString('ko-KR') }}</span>
        </div>
      </header>
      <h4 v-if="post.title" class="post-title">{{ post.title }}</h4>
      <p class="post-body">{{ post.content }}</p>
    </div>
    <footer class="post-foot">
      <button class="like" :class="{ active: liked, bounce }" type="button" @click="toggleLike">
        {{ liked ? '♥' : '♡' }} <span class="num">{{ likeCount }}</span>
      </button>
      <span class="comments num">💬 {{ post.comment_count }}</span>
    </footer>
  </article>
</template>

<style scoped>
.post {
  background: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: rgba(0, 0, 0, 0.7);
  --text-tertiary: rgba(0, 0, 0, 0.5);
  color: var(--text-primary);
}
.post-click {
  cursor: pointer;
}
.post-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: var(--space-3);
}
.meta {
  display: flex;
  flex-direction: column;
}
.name {
  font-weight: 700;
  font-size: 14px;
}
.date {
  font-size: 12px;
  color: var(--text-tertiary);
}
.post-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 6px;
}
.post-body {
  color: var(--text-secondary);
  line-height: 1.7;
  white-space: pre-line;
}
.post-foot {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-4);
  font-size: 14px;
}
.like {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 14px;
  transition: transform var(--dur-fast);
}
.like.active {
  color: var(--up);
}
.like.bounce {
  animation: heart 0.3s var(--ease-out);
}
@keyframes heart {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}
.comments {
  color: var(--text-tertiary);
}
</style>
