import { http, HttpResponse } from 'msw'

export const handlers = [
  // 프로필 업데이트 (이미지 포함)
  http.patch('/api/v1/accounts/profile/', async () => {
    return HttpResponse.json({
      message: '프로필이 수정되었습니다.',
      profile_image: 'http://localhost:8000/media/profiles/dummy.jpg'
    }, { status: 200 })
  }),
  
  // 비밀번호 변경
  http.post('/api/v1/accounts/password/change/', async () => {
    return HttpResponse.json({ message: '비밀번호가 성공적으로 변경되었습니다.' }, { status: 200 })
  }),
  
  // 오늘의 퀴즈 목록
  http.get('/api/v1/tutors/quizzes/', () => {
    return HttpResponse.json([{
      id: 1,
      question: '다음 중 주식 용어 PER에 대한 설명으로 알맞은 것은?',
      options: ['주가수익비율', '주당순이익', '자기자본이익률'],
      answer: '주가수익비율'
    }])
  }),
]
