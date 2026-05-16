import string
import secrets
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

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