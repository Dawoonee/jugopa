from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    SAFE_METHODS,
    BasePermission,
)
from rest_framework.response import Response
from .models import (
    CommunityPost,
    CommunityComment,
    CommunityPostLike,
    CommunityCommentLike,
)
from .serializers import CommunityPostSerializer, CommunityCommentSerializer


class IsOwnerOrReadOnly(BasePermission):
    """조회는 누구나, 수정/삭제는 작성자 본인만 허용한다."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class CommunityPostViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects.all().order_by('-created_at')
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # 종목별 커뮤니티: ?stock=<종목코드>로 해당 종목 글만 필터링
    def get_queryset(self):
        queryset = super().get_queryset()
        stock_code = self.request.query_params.get('stock')
        if stock_code is not None:
            queryset = queryset.filter(stock__stock_code=stock_code)
        return queryset

    # 게시글 생성 시 현재 요청을 보낸 유저를 작성자로 자동 지정
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """좋아요 토글 — 이미 눌렀으면 취소, 아니면 추가. {liked, like_count} 반환."""
        post = self.get_object()
        like, created = CommunityPostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        return Response({
            'liked': created,
            'like_count': post.likes.count(),
        }, status=status.HTTP_200_OK)


class CommunityCommentViewSet(viewsets.ModelViewSet):
    queryset = CommunityComment.objects.all()
    serializer_class = CommunityCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """댓글 좋아요 토글 — 이미 눌렀으면 취소, 아니면 추가. {liked, like_count} 반환."""
        comment = self.get_object()
        like, created = CommunityCommentLike.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()
        return Response({
            'liked': created,
            'like_count': comment.likes.count(),
        }, status=status.HTTP_200_OK)