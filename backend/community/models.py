from django.db import models
from django.conf import settings

class CommunityPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="작성자"
    )
    # null이면 전역 게시글, 값이 있으면 해당 종목 커뮤니티 게시글
    stock = models.ForeignKey(
        'stocks.Stock',
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
        verbose_name="종목",
    )
    title = models.CharField(max_length=255, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'community_post'
        verbose_name = '게시글'
        verbose_name_plural = '게시글 목록'

    def __str__(self):
        return self.title


class CommunityComment(models.Model):
    post = models.ForeignKey(
        CommunityPost, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name="게시글"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name="작성자"
    )
    content = models.TextField(verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'community_comment'
        verbose_name = '댓글'
        verbose_name_plural = '댓글 목록'

    def __str__(self):
        return f"{self.user.username}의 댓글: {self.content[:20]}"


class CommunityPostLike(models.Model):
    """게시글 좋아요 — 사용자당 게시글 1회."""
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes', verbose_name="게시글")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes', verbose_name="사용자")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_like'
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} ♥ {self.post_id}"


class CommunityCommentLike(models.Model):
    """댓글 좋아요 — 사용자당 댓글 1회."""
    comment = models.ForeignKey(CommunityComment, on_delete=models.CASCADE, related_name='likes', verbose_name="댓글")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_likes', verbose_name="사용자")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_comment_like'
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user.username} ♥ comment {self.comment_id}"