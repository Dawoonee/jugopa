import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { chatbotApi } from '@/api/chatbot'
import { tokenStore } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const STORAGE_KEY = 'jugopa_chat'
const WELCOME_TEXT = '주고파에 와주셔서 감사합니다! 무엇이 궁금하세요?'

// sessionStorage → 페이지 이동·새로고침엔 유지되고, 탭을 닫으면 사라진다.
function loadState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useChatbotStore = defineStore('chatbot', () => {
  const saved = loadState()
  const isOpen = ref(saved?.isOpen ?? false)
  const messages = ref(saved?.messages ?? []) // [{ role: 'user'|'assistant', text, meta? }]
  // 이미 대화가 있으면 연결된 상태로 복원, 없으면 첫 오픈 시 연결 절차를 밟는다
  const status = ref(messages.value.length ? 'ready' : 'idle') // 'idle' | 'connecting' | 'ready'
  const sending = ref(false)

  // 대화/열림 상태를 세션에 저장
  watch(
    [isOpen, messages],
    () => {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ isOpen: isOpen.value, messages: messages.value }))
      } catch {
        /* 저장 실패는 무시 (시크릿 모드 등) */
      }
    },
    { deep: true },
  )

  // 로그인/로그아웃 시 대화 초기화
  watch(() => useAuthStore().isAuthenticated, () => {
    reset()
  })

  function reset() {
    messages.value = []
    status.value = 'idle'
    sending.value = false
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      /* 무시 */
    }
  }

  async function connect() {
    status.value = 'connecting'
    try {
      await chatbotApi.health()
    } catch {
      /* 헬스 체크 실패해도 사용 시도는 허용 (실제 전송 시 에러 안내) */
    }
    status.value = 'ready'
    if (!messages.value.length) {
      messages.value.push({ role: 'assistant', text: WELCOME_TEXT, meta: true })
    }
  }

  function open() {
    isOpen.value = true
    if (status.value === 'idle') connect()
  }

  function close() {
    isOpen.value = false // 대화는 유지
  }

  function toggle() {
    if (isOpen.value) close()
    else open()
  }

  async function send(text) {
    const content = text.trim()
    if (!content || sending.value || status.value !== 'ready') return

    // 백엔드로 보낼 history: 로컬 안내 메시지(meta)는 제외
    const history = messages.value
      .filter((m) => !m.meta)
      .map((m) => ({ role: m.role, content: m.text }))

    messages.value.push({ role: 'user', text: content })
    sending.value = true
    try {
      const { data } = await chatbotApi.send(content, history)
      messages.value.push({ role: 'assistant', text: data.reply })
    } catch {
      messages.value.push({
        role: 'assistant',
        text: '죄송해요, 답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요.',
        meta: true,
      })
    } finally {
      sending.value = false
    }
  }

  return { isOpen, messages, status, sending, open, close, toggle, send, reset }
})
