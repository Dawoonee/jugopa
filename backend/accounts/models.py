from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    interest_sectors = models.ManyToManyField(
        'news.Sector', blank=True, related_name='interested_users', verbose_name="관심 업종"
    )
    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers', blank=True, verbose_name="팔로잉"
    )
    investment_type = models.CharField(
        max_length=5, blank=True, null=True, verbose_name="주식 성향"
    )

    def __str__(self):
        return self.username


class UserDailyVisit(models.Model):
    """마이페이지 '오늘 방문' 통계용 — 사용자별 일자 단위 방문 기록."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_visits')
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"