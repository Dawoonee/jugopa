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
  updateProfileImage(file) {
    const fd = new FormData()
    fd.append('profile_image', file)
    return client.patch('accounts/profile/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  changePassword(payload) {
    return client.post('accounts/profile/password/', payload)
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
  getFollows() {
    return client.get('accounts/profile/follows/')
  },
}
