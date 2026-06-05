from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
import random

from .models import Term, DailyTerm, Quiz, UserQuizHistory, UserTermReadHistory
from .serializers import (
    TermSerializer, DailyTermSerializer, 
    QuizSerializer, UserQuizHistorySerializer
)

# ... (기존 TermViewSet, QuizViewSet 등은 유지) ...

class DailyTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyTerm.objects.all().order_by('-date')
    serializer_class = DailyTermSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """오늘의 용어 반환 (없으면 랜덤 생성)"""
        today_date = timezone.now().date()
        daily_term = DailyTerm.objects.filter(date=today_date).first()

        if not daily_term:
            terms = list(Term.objects.all())
            if terms:
                random_term = random.choice(terms)
                daily_term = DailyTerm.objects.create(date=today_date, term=random_term)
            else:
                return Response({"detail": "DB에 용어가 없습니다."}, status=404)

        serializer = self.get_serializer(daily_term)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def read(self, request, pk=None):
        """사용자가 용어를 읽었다고 체크"""
        daily_term = self.get_object()
        
        UserTermReadHistory.objects.get_or_create(
            user=request.user,
            term=daily_term.term
        )
        return Response({"detail": "열람 기록이 정상적으로 저장되었습니다."})


class ReviewQuizViewSet(viewsets.ViewSet):
    """읽은 용어 기반 복습 퀴즈 뷰셋"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def questions(self, request):
        """사용자가 읽은 용어의 설명(문제) 제공"""
        read_histories = UserTermReadHistory.objects.filter(user=request.user).select_related('term')
        
        questions = []
        for history in read_histories:
            questions.append({
                "term_id": history.term.id,
                "explanation": history.term.explanation
            })
        
        random.shuffle(questions) # 문제 순서 섞기
        return Response(questions)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """주관식 정답 채점"""
        term_id = request.data.get('term_id')
        user_answer = request.data.get('answer', '').strip() # 공백 제거

        try:
            term = Term.objects.get(id=term_id)
            is_correct = (term.term_name == user_answer)
            
            return Response({
                "is_correct": is_correct,
                "correct_answer": term.term_name
            })
        except Term.DoesNotExist:
            return Response({"detail": "존재하지 않는 용어입니다."}, status=404)