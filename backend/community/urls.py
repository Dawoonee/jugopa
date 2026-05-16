from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'community'

router = DefaultRouter()
router.register(r'posts', views.CommunityPostViewSet)
router.register(r'comments', views.CommunityCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]