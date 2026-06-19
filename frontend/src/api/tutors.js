import client from './client'

export const tutorsApi = {
  dailyTerm() {
    return client.get('tutors/daily-terms/today/')
  },
  quizzes() {
    return client.get('tutors/quizzes/')
  },
  checkQuiz(quizId, answer) {
    return client.post(`tutors/quizzes/${quizId}/check/`, { answer })
  },
}
