import client from './client'

export const authApi = {
  signup(payload) {
    return client.post('accounts/signup/', payload)
  },
  login(payload) {
    return client.post('accounts/login/', payload)
  },
  randomPassword() {
    return client.get('accounts/random-password/')
  },
  getProfile() {
    return client.get('accounts/profile/')
  },
  updateProfile(payload) {
    return client.patch('accounts/profile/', payload)
  },
  deleteProfile() {
    return client.delete('accounts/profile/')
  },
  getStats() {
    return client.get('accounts/profile/stats/')
  },
  quizCalendar() {
    return client.get('accounts/profile/quiz-calendar/')
  },
}
