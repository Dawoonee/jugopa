import client from '@/api/client'

export const chatbotApi = {
  // 가드레일 통과 시 답변, 부적절하면 거절 문구를 reply 로 받는다
  send(message, history) {
    return client.post('chatbot/chat/', { message, history })
  },
  // '연결중' 상태 해제용 헬스 체크
  health() {
    return client.get('chatbot/health/')
  },
}
