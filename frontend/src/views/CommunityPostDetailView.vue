<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { communityApi } from '@/api/community'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import Skeleton from '@/components/common/Skeleton.vue'
import UserProfileModal from '@/components/UserProfileModal.vue'
import { useWeatherTheme } from '@/composables/useWeatherTheme'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const postId = route.params.postId
const post = ref(null)
const loading = ref(true)

// 게시글 수정/삭제
const editingPost = ref(false)
const draft = ref({ title: '', content: '' })
const showDelete = ref(false)

// 프로필 모달
const showProfile = ref(false)
const targetNickname = ref('')

function openProfile(nickname) {
  if (nickname) {
    targetNickname.value = nickname
    showProfile.value = true
  }
}

// 댓글
const newComment = ref('')
const editingCommentId = ref(null)
const commentDraft = ref('')
const delCommentId = ref(null)

const isPostOwner = computed(() => post.value && auth.user?.id === post.value.user)
const comments = computed(() => post.value?.comments || [])

const { fetchWeather, themeClass, bgStyle } = useWeatherTheme()

onMounted(async () => {
  if (!auth.user) await auth.fetchProfile().catch(() => {})
  await loadPost()
})

async function loadPost() {
  loading.value = true
  try {
    const { data } = await communityApi.post(postId)
    post.value = data
    await fetchWeather()
  } catch (e) {
    post.value = null
  } finally {
    loading.value = false
  }
}

function isCommentOwner(c) {
  return auth.user?.id === c.user
}

function requireAuth() {
  if (!auth.isAuthenticated) {
    toast.show('로그인이 필요해요', 'error')
    return false
  }
  return true
}

// ── 게시글 좋아요 ─────────────────────────────
async function togglePostLike() {
  if (!requireAuth()) return
  try {
    const { data } = await communityApi.toggleLike(post.value.id)
    post.value.liked = data.liked
    post.value.like_count = data.like_count
  } catch (e) {
    toast.show('처리에 실패했어요', 'error')
  }
}

// ── 게시글 수정/삭제 ──────────────────────────
function startEditPost() {
  draft.value = { title: post.value.title, content: post.value.content }
  editingPost.value = true
}

async function savePost() {
  if (!draft.value.content.trim()) return
  try {
    const { data } = await communityApi.updatePost(post.value.id, {
      title: draft.value.title || '제목 없음',
      content: draft.value.content,
    })
    post.value = data
    editingPost.value = false
    toast.show('글을 수정했어요', 'success')
  } catch (e) {
    toast.show('수정에 실패했어요', 'error')
  }
}

async function removePost() {
  try {
    await communityApi.deletePost(post.value.id)
    toast.show('글을 삭제했어요')
    router.push({ name: 'stock-community', params: { code: route.params.code } })
  } catch (e) {
    toast.show('삭제에 실패했어요', 'error')
  }
}

// ── 댓글 CRUD ────────────────────────────────
async function addComment() {
  if (!requireAuth()) return
  if (!newComment.value.trim()) return
  try {
    const { data } = await communityApi.createComment(post.value.id, newComment.value.trim())
    post.value.comments.push(data)
    post.value.comment_count = (post.value.comment_count || 0) + 1
    newComment.value = ''
  } catch (e) {
    toast.show('댓글 등록에 실패했어요', 'error')
  }
}

function startEditComment(c) {
  editingCommentId.value = c.id
  commentDraft.value = c.content
}

function cancelEditComment() {
  editingCommentId.value = null
  commentDraft.value = ''
}

async function saveComment(c) {
  if (!commentDraft.value.trim()) return
  try {
    const { data } = await communityApi.updateComment(c.id, commentDraft.value.trim())
    Object.assign(c, data)
    cancelEditComment()
    toast.show('댓글을 수정했어요', 'success')
  } catch (e) {
    toast.show('댓글 수정에 실패했어요', 'error')
  }
}

async function removeComment(c) {
  try {
    await communityApi.deleteComment(c.id)
    post.value.comments = post.value.comments.filter((x) => x.id !== c.id)
    post.value.comment_count = Math.max(0, (post.value.comment_count || 1) - 1)
    toast.show('댓글을 삭제했어요')
  } catch (e) {
    toast.show('댓글 삭제에 실패했어요', 'error')
  }
}

async function toggleCommentLike(c) {
  if (!requireAuth()) return
  try {
    const { data } = await communityApi.toggleCommentLike(c.id)
    c.liked = data.liked
    c.like_count = data.like_count
  } catch (e) {
    toast.show('처리에 실패했어요', 'error')
  }
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('ko-KR') : ''
}
</script>

<template>
  <div class="page post-detail" :class="themeClass">
    <div class="weather-bg" :style="bgStyle"></div>
    <button class="back" type="button" @click="router.back()">‹ 뒤로</button>

    <div v-if="loading" class="card">
      <Skeleton height="22px" width="50%" />
      <div style="height: 16px" />
      <Skeleton v-for="n in 3" :key="n" height="18px" />
    </div>

    <template v-else-if="post">
      <!-- 게시글 -->
      <article class="card post">
        <header class="post-head">
          <div class="meta">
            <span class="name profile-trigger-text" @click="openProfile(post.nickname || post.username)">
              {{ post.nickname || post.username }}
            </span>
            <span class="date num">{{ formatDate(post.created_at) }}</span>
          </div>
          <div v-if="isPostOwner && !editingPost" class="owner-actions">
            <button class="link-btn" type="button" @click="startEditPost">수정</button>
            <button class="link-btn danger" type="button" @click="showDelete = true">삭제</button>
          </div>
        </header>

        <template v-if="!editingPost">
          <h1 v-if="post.title" class="title">{{ post.title }}</h1>
          <p class="body">{{ post.content }}</p>
        </template>
        <div v-else class="edit-form">
          <BaseInput v-model="draft.title" label="제목" placeholder="제목을 입력하세요" />
          <label class="field">
            <span class="field-label">내용</span>
            <textarea v-model="draft.content" class="textarea" rows="5" />
          </label>
          <div class="edit-actions">
            <BaseButton variant="ghost" @click="editingPost = false">취소</BaseButton>
            <BaseButton @click="savePost">저장</BaseButton>
          </div>
        </div>

        <footer v-if="!editingPost" class="post-foot">
          <button class="like" :class="{ active: post.liked }" type="button" @click="togglePostLike">
            {{ post.liked ? '♥' : '♡' }} <span class="num">{{ post.like_count }}</span>
          </button>
          <span class="cnt num">💬 {{ post.comment_count }}</span>
        </footer>
      </article>

      <!-- 댓글 -->
      <section class="comments">
        <h2 class="block-title">댓글 {{ post.comment_count }}</h2>

        <div v-if="auth.isAuthenticated" class="comment-write">
          <textarea
            v-model="newComment"
            class="textarea"
            rows="2"
            placeholder="댓글을 입력하세요"
          />
          <BaseButton :disabled="!newComment.trim()" @click="addComment">등록</BaseButton>
        </div>
        <p v-else class="muted">댓글을 작성하려면 로그인하세요.</p>

        <ul v-if="comments.length" class="comment-list">
          <li v-for="c in comments" :key="c.id" class="comment card">
            <div class="comment-head">
              <span class="name profile-trigger-text" @click="openProfile(c.nickname || c.username)">
                {{ c.nickname || c.username }}
              </span>
              <span class="date num">{{ formatDate(c.created_at) }}</span>
            </div>

            <template v-if="editingCommentId !== c.id">
              <p class="comment-body">{{ c.content }}</p>
              <div class="comment-foot">
                <button class="like sm" :class="{ active: c.liked }" type="button" @click="toggleCommentLike(c)">
                  {{ c.liked ? '♥' : '♡' }} <span class="num">{{ c.like_count }}</span>
                </button>
                <div v-if="isCommentOwner(c)" class="owner-actions">
                  <button class="link-btn" type="button" @click="startEditComment(c)">수정</button>
                  <button class="link-btn danger" type="button" @click="removeComment(c)">삭제</button>
                </div>
              </div>
            </template>
            <div v-else class="comment-edit">
              <textarea v-model="commentDraft" class="textarea" rows="2" />
              <div class="edit-actions">
                <BaseButton variant="ghost" @click="cancelEditComment">취소</BaseButton>
                <BaseButton @click="saveComment(c)">저장</BaseButton>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="muted">아직 댓글이 없어요. 첫 댓글을 남겨보세요!</p>
      </section>
    </template>

    <BaseModal v-if="showDelete" v-model="showDelete" title="">
      <div class="confirm">
        <div class="warn">🗑️</div>
        <h3 class="c-title">게시글을 삭제할까요?</h3>
        <p class="c-desc">삭제 후에는 복구할 수 없습니다.</p>
      </div>
      <template #footer>
        <BaseButton variant="ghost" block @click="showDelete = false">취소</BaseButton>
        <BaseButton variant="destructive" block @click="removePost">삭제</BaseButton>
      </template>
    </BaseModal>

    <UserProfileModal v-if="showProfile" :nickname="targetNickname" @close="showProfile = false" />
  </div>
</template>

<style scoped>
.back {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 14px;
  margin-bottom: var(--space-4);
}
.back:hover {
  color: var(--accent);
}
.post {
  margin-bottom: var(--space-5);
}
.post-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}
.profile-trigger-text {
  cursor: pointer;
}
.profile-trigger-text:hover {
  text-decoration: underline;
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
.title {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: var(--space-3);
}
.body {
  color: var(--text-secondary);
  line-height: 1.8;
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
}
.like.active {
  color: var(--up);
}
.like.sm {
  font-size: 13px;
}
.cnt {
  color: var(--text-tertiary);
}
.owner-actions {
  display: flex;
  gap: var(--space-3);
}
.link-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 600;
}
.link-btn:hover {
  color: var(--accent);
}
.link-btn.danger:hover {
  color: var(--danger);
}
.block-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: var(--space-4);
}
.comment-write {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  margin-bottom: var(--space-4);
}
.comment-write .textarea {
  flex: 1;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.comment {
  padding: var(--space-3) var(--space-4);
}
.comment-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.comment-body {
  color: var(--text-primary);
  line-height: 1.7;
  white-space: pre-line;
}
.comment-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.comment-edit {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
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
  padding: 12px 14px;
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
.muted {
  color: var(--text-tertiary);
  font-size: 14px;
}
.confirm {
  text-align: center;
  padding: var(--space-3) 0;
}
.warn {
  font-size: 40px;
}
.c-title {
  margin-top: var(--space-3);
  font-size: 18px;
  font-weight: 800;
}
.c-desc {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
