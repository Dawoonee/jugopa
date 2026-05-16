from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Term, DailyTerm, Quiz, UserQuizHistory
from .serializers import (
    TermSerializer, DailyTermSerializer, 
    QuizSerializer, UserQuizHistorySerializer
)

# 일반 유저는 조회만 가능 (데이터 수정은 Django Admin에서 수행)
class TermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

class DailyTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyTerm.objects.all().order_by('-date')
    serializer_class = DailyTermSerializer

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

# 퀴즈 풀이 이력은 로그인한 유저만 생성 및 자신의 이력 조회 가능
class UserQuizHistoryViewSet(mixins.CreateModelMixin, 
                             mixins.ListModelMixin, 
                             viewsets.GenericViewSet):
    serializer_class = UserQuizHistorySerializer
    permission_classes = [IsAuthenticated]

    # 본인이 푼 퀴즈 이력만 반환
    def get_queryset(self):
        return UserQuizHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)