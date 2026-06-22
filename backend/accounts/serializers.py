from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from news.models import Sector

# config/settings.py에 설정된 AUTH_USER_MODEL을 가져옵니다.
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    마이페이지 조회 및 수정용 시리얼라이저 [F003]
    """
    # 읽기: 관심 업종명 리스트 / 쓰기: 섹터 id 리스트
    interest_sectors = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.filter(level=Sector.Level.LARGE), many=True, required=False
    )
    interest_sector_names = serializers.SerializerMethodField()
    # 업로드(파일) + 삭제(null) 모두 허용
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'created_at',
                  'profile_image', 'interest_sectors', 'interest_sector_names', 'investment_type')
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
        queryset=Sector.objects.filter(level=Sector.Level.LARGE), many=True, required=False
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


class PasswordChangeSerializer(serializers.Serializer):
    """
    비밀번호 변경용 시리얼라이저 [F003]
    현재 비밀번호 확인 후 새 비밀번호로 변경
    """
    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('현재 비밀번호가 일치하지 않습니다.')
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user