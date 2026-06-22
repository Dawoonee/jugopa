<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'
import chatBotImg from '@/assets/chat_bot.png'

const chat = useChatbotStore()
const draft = ref('')
const listRef = ref(null)

function scrollToBottom() {
  nextTick(() => {
    const el = listRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

// 새 메시지 / 팝업 열림 시 맨 아래로 스크롤
watch(() => chat.messages.length, scrollToBottom)
watch(
  () => chat.isOpen,
  (open) => {
    if (open) scrollToBottom()
  },
)

function onSubmit() {
  const text = draft.value
  if (!text.trim() || chat.sending || chat.status !== 'ready') return
  draft.value = ''
  chat.send(text)
}
</script>

<template>
  <div class="chatbot">
    <!-- 떠 있는 챗봇 패널: 페이지를 이동해도 닫기 전까지 유지된다 -->
    <transition name="panel">
      <section v-if="chat.isOpen" class="panel" role="dialog" aria-label="주고파 챗봇">
        <header class="panel-head">
          <span class="panel-title">
            <img :src="chatBotImg" alt="" class="panel-title-img" />
            주고파 챗봇
          </span>
          <button class="panel-close" type="button" aria-label="닫기" @click="chat.close()">✕</button>
        </header>

        <div ref="listRef" class="panel-body">
          <!-- 연결 중: 안내 문구 + 입력 잠금 -->
          <p v-if="chat.status === 'connecting'" class="msg msg--system">잠시만 기다려 주세요..</p>

          <template v-else>
            <div
              v-for="(m, i) in chat.messages"
              :key="i"
              class="msg"
              :class="m.role === 'user' ? 'msg--user' : 'msg--bot'"
            >
              {{ m.text }}
            </div>
            <p v-if="chat.sending" class="msg msg--bot msg--typing">답변을 작성하고 있어요…</p>
          </template>
        </div>

        <form class="panel-input" @submit.prevent="onSubmit">
          <input
            v-model="draft"
            type="text"
            class="panel-text"
            :placeholder="chat.status === 'connecting' ? '연결 중입니다…' : '메시지를 입력하세요'"
            :disabled="chat.status !== 'ready' || chat.sending"
            autocomplete="off"
          />
          <button class="panel-send" type="submit" :disabled="chat.status !== 'ready' || chat.sending || !draft.trim()">
            전송
          </button>
        </form>
      </section>
    </transition>

    <!-- 플로팅 버튼 -->
    <button class="fab" type="button" :aria-label="chat.isOpen ? '챗봇 닫기' : '챗봇 열기'" @click="chat.toggle()">
      <img :src="chatBotImg" alt="챗봇" class="fab-img" />
    </button>
  </div>
</template>

<style scoped>
.chatbot {
  position: fixed;
  right: var(--space-4);
  bottom: var(--space-4);
  z-index: 40;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-3);
}

/* 플로팅 버튼 */
.fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;
  transition: transform var(--dur-fast) var(--ease-out);
}
.fab:hover {
  transform: translateY(-2px) scale(1.04);
}
.fab-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 팝업 패널 */
.panel {
  width: 340px;
  max-width: calc(100vw - 2 * var(--space-4));
  height: 460px;
  max-height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-lg, 16px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8f9fa;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: 700;
  color: #1a1a1a;
}
.panel-title-img {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  object-fit: cover;
}
.panel-close {
  border: none;
  background: transparent;
  color: #8b95a1;
  font-size: 15px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}
.panel-close:hover {
  color: #1a1a1a;
  background: rgba(0, 0, 0, 0.05);
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.msg {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.msg--bot {
  align-self: flex-start;
  background: #f0f2f5;
  color: #1a1a1a;
  border-bottom-left-radius: 4px;
}
.msg--user {
  align-self: flex-end;
  background: var(--accent);
  color: var(--text-on-accent);
  border-bottom-right-radius: 4px;
}
.msg--system {
  align-self: center;
  background: transparent;
  color: #8b95a1;
  font-size: 13px;
}
.msg--typing {
  color: #8b95a1;
  font-style: italic;
}

.panel-input {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}
.panel-text {
  flex: 1;
  height: 38px;
  padding: 0 12px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(0, 0, 0, 0.15);
  background: #ffffff;
  color: #1a1a1a;
  font-size: 14px;
}
.panel-text:focus {
  outline: none;
  border-color: var(--accent);
}
.panel-text:disabled {
  opacity: 0.6;
}
.panel-send {
  height: 38px;
  padding: 0 14px;
  border-radius: var(--radius-pill);
  border: none;
  background: var(--accent);
  color: var(--text-on-accent);
  font-weight: 700;
  cursor: pointer;
}
.panel-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 패널 등장/퇴장 */
.panel-enter-active,
.panel-leave-active {
  transition:
    opacity var(--dur-base) var(--ease-out),
    transform var(--dur-base) var(--ease-out);
}
.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}

/* 모바일: 하단 탭바 위로 띄운다 */
@media (max-width: 767px) {
  .chatbot {
    bottom: calc(var(--bottom-tab-height) + var(--space-3) + env(safe-area-inset-bottom, 0px));
  }
  .fab {
    width: 56px;
    height: 56px;
  }
}
</style>
