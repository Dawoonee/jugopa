from rest_framework import serializers
from .models import CommunityPost, CommunityComment

class CommunityCommentSerializer(serializers.ModelSerializer):
    # 읽기 전용으로 작성자 닉네임 노출
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = CommunityComment
        fields = ['id', 'post', 'user', 'username', 'content', 'created_at']
        read_only_fields = ['post', 'user'] # post와 user는 뷰에서 자동 주입


class CommunityPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    # 게시글 조회 시 달린 댓글들도 함께 보여주기 위해 중첩 시리얼라이저 사용
    comments = CommunityCommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'username', 'title', 'content', 'created_at', 'updated_at', 'comments', 'comment_count']
        read_only_fields = ['user']