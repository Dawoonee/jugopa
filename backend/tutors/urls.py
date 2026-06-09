from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tutors'

router = DefaultRouter()
router.register(r'terms', views.TermViewSet)
router.register(r'daily-terms', views.DailyTermViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'quiz-history', views.UserQuizHistoryViewSet, basename='quiz-history')
router.register(r'review-quiz', views.ReviewQuizViewSet, basename='review-quiz')
urlpatterns = [
    path('', include(router.urls)),
]