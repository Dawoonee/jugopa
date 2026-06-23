import { createRouter, createWebHistory } from 'vue-router'
import { tokenStore } from '@/api/client'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/recommend', name: 'recommend', component: () => import('@/views/RecommendView.vue') },
  {
    path: '/indices/:name',
    name: 'index-detail',
    component: () => import('@/views/IndexDetailView.vue'),
  },
  {
    path: '/sectors/:id',
    name: 'sector-detail',
    component: () => import('@/views/SectorDetailView.vue'),
  },
  {
    path: '/recommend/card/:id',
    name: 'card-news-detail',
    component: () => import('@/views/CardNewsDetailView.vue'),
  },
  {
    path: '/recommend/:code',
    name: 'stock-detail',
    component: () => import('@/views/StockDetailView.vue'),
  },
  {
    path: '/recommend/:code/community',
    name: 'stock-community',
    component: () => import('@/views/StockCommunityView.vue'),
  },
  {
    path: '/recommend/:code/community/:postId',
    name: 'community-post-detail',
    component: () => import('@/views/CommunityPostDetailView.vue'),
  },
  { path: '/knowledge', name: 'knowledge', component: () => import('@/views/KnowledgeView.vue') },
  { path: '/knowledge/quiz', name: 'quiz', component: () => import('@/views/QuizView.vue') },
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/test',
    name: 'investment-test',
    component: () => import('@/views/InvestmentTestView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/signup', name: 'signup', component: () => import('@/views/SignupView.vue'), meta: { guestOnly: true } },
  { path: '/landing', name: 'landing', component: () => import('@/views/LandingView.vue') },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to, from) => {
  const agreedToTerms = localStorage.getItem('agreedToTerms') === 'true'
  
  if (!agreedToTerms && to.name !== 'landing') {
    return { name: 'landing' }
  }

  const authed = !!tokenStore.access
  if (to.meta.requiresAuth && !authed) {
    import('@/stores/auth').then(({ useAuthStore }) => {
      const auth = useAuthStore()
      auth.showLoginModal = true
    })
    // If it's a direct visit (no previous route), go home. Otherwise stay on the current page.
    return from.name ? false : { name: 'home' }
  }
  if (to.meta.guestOnly && authed) {
    return { name: 'home' }
  }
})

export default router
