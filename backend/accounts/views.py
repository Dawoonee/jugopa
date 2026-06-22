import string
import secrets
from datetime import timedelta
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserDailyVisit
from .serializers import RegisterSerializer, UserSerializer, PasswordChangeSerializer
from tutors.models import UserQuizHistory, DailyTerm

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    회원가입 뷰 [F001]
    누구나 접근 가능해야 하므로 AllowAny 설정
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    마이페이지(조회, 수정, 탈퇴) 뷰 [F003]
    - GET: 내 정보 조회
    - PUT/PATCH: 닉네임, 이메일 등 수정
    - DELETE: 회원 탈퇴
    로그인한 유저만 접근 가능 (IsAuthenticated)
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    # URL에서 pk를 받지 않고, 현재 토큰으로 인증된 유저 객체를 바로 반환
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    비밀번호 변경 뷰 [F003]
    현재 비밀번호를 확인하고 새 비밀번호로 변경. 로그인한 유저만 접근 가능.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ProfileStatsView(APIView):
    """마이페이지 통계 [F003] — 관심종목 수 / 퀴즈 참여 횟수 / 오늘 방문 여부.

    호출 시 오늘 방문 기록(UserDailyVisit)을 남긴다.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        _, created = UserDailyVisit.objects.get_or_create(user=user, date=today)
        return Response({
            'bookmark_count': user.bookmarks.count(),
            'quiz_count': user.quiz_histories.count(),
            'follower_count': user.followers.count(),
            'following_count': user.following.count(),
            'today_visited': True,            # 이 요청으로 오늘 방문이 보장됨
            'first_visit_today': created,     # 오늘 첫 방문이면 True
        })


class QuizCalendarView(APIView):
    """성취도(달력+메달)용 — 날짜별 퀴즈 풀이 집계와 연속 풀이 스트릭을 반환한다.

    반환: { total_solved, current_streak, longest_streak, daily: [{date, count}] }
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        # 하루 1건 제약이 있으므로 풀이 이력 = 날짜별 1건. 용어/퀴즈 상세까지 함께 내려준다.
        histories = (
            UserQuizHistory.objects
            .filter(user=user)
            .select_related('quiz')
            .order_by('solved_date')
        )

        # 풀이한 날짜의 '오늘의 용어'를 한 번에 매핑 (date → DailyTerm.term)
        solved_dates = [h.solved_date for h in histories]
        term_by_date = {
            dt.date: dt.term
            for dt in DailyTerm.objects.filter(date__in=solved_dates).select_related('term')
        }

        daily = []
        for h in histories:
            term = term_by_date.get(h.solved_date)
            daily.append({
                'date': h.solved_date.isoformat(),
                'count': 1,
                'term_name': term.term_name if term else '',
                'term_explanation': term.explanation if term else '',
                'is_correct': h.is_correct,
                'user_choice': h.user_choice,
                'answer': h.quiz.answer,
                'question': h.quiz.question,
                'options': h.quiz.options,
                'explanation': h.quiz.explanation,
            })
        total_solved = len(daily)
        date_set = {h.solved_date for h in histories}

        # 최장 연속 풀이일 계산
        longest_streak = 0
        run = 0
        prev = None
        for day in sorted(date_set):
            run = run + 1 if (prev is not None and day == prev + timedelta(days=1)) else 1
            longest_streak = max(longest_streak, run)
            prev = day

        # 현재 연속 풀이일 (오늘 또는 어제부터 거슬러 계산)
        today = timezone.localdate()
        cursor = today if today in date_set else today - timedelta(days=1)
        current_streak = 0
        while cursor in date_set:
            current_streak += 1
            cursor -= timedelta(days=1)

        return Response({
            'total_solved': total_solved,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'daily': daily,
        })


class GenerateRandomPasswordView(APIView):
    """
    비밀번호 난수 자동 생성 및 추천 뷰 [F001]
    회원가입 시 프론트엔드에서 이 API를 호출하여 안전한 비밀번호를 추천받음
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        # 대소문자, 숫자, 특수문자를 포함한 12자리 난수 생성 로직
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)):
                break
                
        return Response({'recommended_password': password}, status=status.HTTP_200_OK)


class UserProfileDetailView(APIView):
    """
    타 유저 프로필 조회 (프로필 사진, 닉네임, 관심 업종, 관심 종목, 팔로워/팔로잉 등)
    """
    permission_classes = (AllowAny,)

    def get(self, request, nickname):
        target_user = generics.get_object_or_404(User, nickname=nickname)
        
        interest_sectors = [{'id': s['id'], 'sector_name': s['name']} for s in target_user.interest_sectors.values('id', 'name')]
        bookmarks = list(target_user.bookmarks.select_related('stock').values(
            'stock__stock_code', 'stock__stock_name'
        ))
        
        is_following = False
        if request.user.is_authenticated:
            is_following = request.user.following.filter(id=target_user.id).exists()
            
        return Response({
            'nickname': target_user.nickname,
            'profile_image': request.build_absolute_uri(target_user.profile_image.url) if target_user.profile_image else None,
            'interest_sectors': interest_sectors,
            'interest_stocks': bookmarks,
            'follower_count': target_user.followers.count(),
            'following_count': target_user.following.count(),
            'is_following': is_following,
        }, status=status.HTTP_200_OK)


class UserFollowView(APIView):
    """
    특정 유저 팔로우/언팔로우 토글
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, nickname):
        target_user = generics.get_object_or_404(User, nickname=nickname)
        if target_user == request.user:
            return Response({'detail': '자기 자신은 팔로우할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_following = request.user.following.filter(id=target_user.id).exists()
        if is_following:
            request.user.following.remove(target_user)
        else:
            request.user.following.add(target_user)
            
        return Response({
            'following': not is_following,
            'follower_count': target_user.followers.count(),
            'following_count': target_user.following.count(),
        })

class UserFollowListView(APIView):
    """
    내 팔로워 및 팔로잉 목록 조회
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        followers = [{'nickname': u.nickname, 'profile_image': request.build_absolute_uri(u.profile_image.url) if u.profile_image else None} for u in user.followers.all()]
        following = [{'nickname': u.nickname, 'profile_image': request.build_absolute_uri(u.profile_image.url) if u.profile_image else None} for u in user.following.all()]

        return Response({
            'followers': followers,
            'following': following
        })