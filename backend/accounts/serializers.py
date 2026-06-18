from rest_framework import serializers
from django.contrib.auth import get_user_model

from news.models import Sector

# config/settings.py에 설정된 AUTH_USER_MODEL을 가져옵니다.
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    마이페이지 조회 및 수정용 시리얼라이저 [F003]
    """
    # 읽기: 관심 업종명 리스트 / 쓰기: 섹터 id 리스트
    interest_sectors = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.all(), many=True, required=False
    )
    interest_sector_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'created_at',
                  'interest_sectors', 'interest_sector_names')
        # id, username, 생성일은 수정할 수 없도록 읽기 전용 처리
        read_only_fields = ('id', 'username', 'created_at')

    def get_interest_sector_names(self, obj):
        return [s.name for s in obj.interest_sectors.all()]


class RegisterSerializer(serializers.ModelSerializer):
    """
    회원가입용 시리얼라이저 [F001]
    """
    # password는 쓰기 전용으로 설정하여 GET 요청 시 노출되지 않도록 함
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    interest_sectors = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'nickname', 'interest_sectors')

    def create(self, validated_data):
        interest_sectors = validated_data.pop('interest_sectors', [])
        # 비밀번호를 평문으로 저장하지 않고 해싱(Hashing)하여 저장하기 위해 create_user 사용
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            nickname=validated_data.get('nickname', '')
        )
        if interest_sectors:
            user.interest_sectors.set(interest_sectors)
        return user