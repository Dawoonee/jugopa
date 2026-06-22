from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원가입 및 비밀번호 추천
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('random-password/', views.GenerateRandomPasswordView.as_view(), name='random_password'),
    
    # JWT 로그인 및 토큰 갱신 (simplejwt 기본 뷰 활용)
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 마이페이지 (조회, 수정, 회원탈퇴가 모두 이 하나의 URL에서 HTTP 메서드(GET, PUT, DELETE)로 처리됨)
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('profile/stats/', views.ProfileStatsView.as_view(), name='profile_stats'),
    path('profile/quiz-calendar/', views.QuizCalendarView.as_view(), name='quiz_calendar'),
    
    # 타 유저 프로필 및 팔로우
    path('profile/follows/', views.UserFollowListView.as_view(), name='user_follows'),
    path('profile/<str:nickname>/', views.UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('profile/<str:nickname>/follow/', views.UserFollowView.as_view(), name='user_follow'),
]