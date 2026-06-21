from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import random

from .models import Term, DailyTerm, Quiz, UserQuizHistory, UserTermReadHistory
from .serializers import (
    TermSerializer, DailyTermSerializer, 
    QuizSerializer, UserQuizHistorySerializer
)

def get_or_create_today_term():
    """오늘 자 DailyTerm을 반환하고, 없으면 전체 용어 중 무작위로 하나 골라 생성한다.

    용어 데이터가 전혀 없으면 None을 반환한다.
    '오늘의 용어'와 '오늘의 퀴즈'가 같은 용어를 가리키도록 양쪽에서 공통 사용한다.
    """
    today_date = timezone.now().date()
    daily_term = DailyTerm.objects.filter(date=today_date).select_related('term').first()
    if not daily_term:
        terms = list(Term.objects.all())
        if not terms:
            return None
        daily_term = DailyTerm.objects.create(date=today_date, term=random.choice(terms))
    return daily_term


# 일반 유저는 조회만 가능 (데이터 수정은 Django Admin에서 수행)
class TermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class DailyTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyTerm.objects.all().order_by('-date')
    serializer_class = DailyTermSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """오늘 자 기준 등록된 오늘의 용어가 있으면 반환하고, 없으면 무작위로 하나 뽑아서 생성 후 반환"""
        daily_term = get_or_create_today_term()
        if not daily_term:
            return Response({"detail": "DB에 용어 데이터가 존재하지 않습니다."}, status=404)

        serializer = self.get_serializer(daily_term)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def read(self, request, pk=None):
        """사용자가 오늘의 용어 페이지에 방문했을 때 열람 이력을 체크(ID 기록)하는 API"""
        daily_term = self.get_object()
        
        # 중복 생성 없이 안전하게 가져오거나 생성(get_or_create)
        UserTermReadHistory.objects.get_or_create(
            user=request.user,
            term=daily_term.term
        )
        return Response({"detail": "용어 열람 기록이 정상적으로 체크되었습니다."})


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """'오늘의 용어'에 해당하는 퀴즈를 반환한다.

        퀴즈 문제는 '… — {용어명}' 형식으로 끝나므로, 오늘의 용어명으로 끝나는 퀴즈를 찾아
        오늘의 용어와 오늘의 퀴즈 주제를 일치시킨다.
        """
        daily_term = get_or_create_today_term()
        if not daily_term:
            return Response({"detail": "DB에 용어 데이터가 존재하지 않습니다."}, status=404)

        term_name = daily_term.term.term_name
        quiz = Quiz.objects.filter(question__endswith=term_name).first()
        if not quiz:
            return Response({"detail": "오늘의 용어에 해당하는 퀴즈가 없습니다."}, status=404)

        serializer = self.get_serializer(quiz)
        data = dict(serializer.data)

        # 로그인 사용자라면 오늘 이미 풀었는지와 그 결과(복습용)를 함께 내려준다.
        data['solved_today'] = False
        data['result'] = None
        if request.user.is_authenticated:
            today = timezone.localdate()
            history = UserQuizHistory.objects.filter(user=request.user, solved_date=today).first()
            if history:
                data['solved_today'] = True
                data['result'] = {
                    'user_choice': history.user_choice,
                    'answer': quiz.answer,
                    'is_correct': history.is_correct,
                    'explanation': quiz.explanation,
                }
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def check(self, request, pk=None):
        """사용자가 고른 보기를 서버에서 채점하고 정답·해설을 반환한다.

        익명 사용자도 채점 가능하며, 로그인 사용자는 하루 1건만 풀이 이력이 기록된다.
        이미 오늘 푼 경우 409와 함께 기존 결과를 반환한다.
        """
        quiz = self.get_object()
        user_answer = request.data.get('answer', '')
        is_correct = (user_answer == quiz.answer)

        # 로그인 사용자는 하루 1건만 기록한다.
        if request.user.is_authenticated:
            today = timezone.localdate()
            existing = UserQuizHistory.objects.filter(user=request.user, solved_date=today).first()
            if existing:
                return Response({
                    "detail": "오늘은 이미 퀴즈를 풀었습니다.",
                    "is_correct": existing.is_correct,
                    "answer": quiz.answer,
                    "explanation": quiz.explanation,
                    "user_choice": existing.user_choice,
                }, status=status.HTTP_409_CONFLICT)

            UserQuizHistory.objects.create(
                user=request.user,
                quiz=quiz,
                is_correct=is_correct,
                user_choice=user_answer,
                solved_date=today,
            )

        return Response({
            "is_correct": is_correct,
            "answer": quiz.answer,
            "explanation": quiz.explanation,
            "user_choice": user_answer,
        })


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


class ReviewQuizViewSet(viewsets.ViewSet):
    """사용자가 열람 체크해 둔 용어의 설명을 문제로 내고 주관식 정답을 맞추는 복습 퀴즈 뷰셋"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def questions(self, request):
        """사용자가 읽었던 용어들의 설명만 모아서 랜덤으로 섞어 퀴즈 목록으로 반환"""
        read_histories = UserTermReadHistory.objects.filter(user=request.user).select_related('term')
        
        questions = []
        for history in read_histories:
            questions.append({
                "term_id": history.term.id,
                "explanation": history.term.explanation
            })
        
        # 문제 무작위 셔플
        random.shuffle(questions)
        return Response(questions)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """사용자가 주관식으로 입력한 텍스트 정답 여부 채점"""
        term_id = request.data.get('term_id')
        user_answer = request.data.get('answer', '').strip() # 앞뒤 공백 제거

        try:
            term = Term.objects.get(id=term_id)
            is_correct = (term.term_name == user_answer)
            
            return Response({
                "is_correct": is_correct,
                "correct_answer": term.term_name
            })
        except Term.DoesNotExist:
            return Response({"detail": "존재하지 않는 용어 번호입니다."}, status=404)