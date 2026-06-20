from rest_framework import serializers
from .models import CommunityPost, CommunityComment

class CommunityCommentSerializer(serializers.ModelSerializer):
    # 읽기 전용으로 작성자 아이디/닉네임 노출
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model = CommunityComment
        fields = ['id', 'post', 'user', 'username', 'nickname', 'content',
                  'created_at', 'updated_at', 'like_count', 'liked']
        read_only_fields = ['post', 'user'] # post와 user는 뷰에서 자동 주입

    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()


class CommunityPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    # 작성자 프로필 이미지(읽기 전용)
    profile_image = serializers.ImageField(source='user.profile_image', read_only=True)
    # 게시글 조회 시 달린 댓글들도 함께 보여주기 위해 중첩 시리얼라이저 사용
    comments = CommunityCommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    # 종목별 커뮤니티: 작성 시 stock_code로 지정, 조회 시 종목명 노출
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'username', 'nickname', 'profile_image', 'stock', 'stock_code', 'stock_name',
                  'title', 'content', 'created_at', 'updated_at',
                  'comments', 'comment_count', 'like_count', 'liked']
        read_only_fields = ['user']

    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()