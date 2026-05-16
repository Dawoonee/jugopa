from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import CommunityPost, CommunityComment
from .serializers import CommunityPostSerializer, CommunityCommentSerializer

class CommunityPostViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects.all().order_by('-created_at')
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 게시글 생성 시 현재 요청을 보낸 유저를 작성자로 자동 지정
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommunityCommentViewSet(viewsets.ModelViewSet):
    queryset = CommunityComment.objects.all()
    serializer_class = CommunityCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 특정 게시글에 달린 댓글만 필터링해서 가져오기 (예: /comments/?post=1)
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post', None)
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    # 댓글 생성 시 요청 유저와, URL이나 payload로 넘어온 게시글 ID 매핑
    def perform_create(self, serializer):
        # 뷰에서 post_id를 직접 넘겨받거나 request.data에서 추출
        post_id = self.request.data.get('post') 
        serializer.save(user=self.request.user, post_id=post_id)