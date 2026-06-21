from django.db import models
from django.conf import settings

class Term(models.Model):
    term_name = models.CharField(max_length=100, unique=True, verbose_name="용어명")
    explanation = models.TextField(verbose_name="용어 설명")

    class Meta:
        db_table = 'term'
        verbose_name = '주식 용어'
        verbose_name_plural = '주식 용어 목록'

    def __str__(self):
        return self.term_name


class DailyTerm(models.Model):
    # 날짜별로 중복된 용어가 들어가지 않도록 unique=True 설정 (무결성 보장)
    date = models.DateField(unique=True, verbose_name="제공 일자")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='daily_terms', verbose_name="용어")

    class Meta:
        db_table = 'daily_term'
        verbose_name = '오늘의 주식 용어'
        verbose_name_plural = '오늘의 주식 용어 목록'

    def __str__(self):
        return f"{self.date} - {self.term.term_name}"


class Quiz(models.Model):
    question = models.TextField(verbose_name="퀴즈 문제")
    # 객관식 선지는 가변적이므로 JSONField 활용 (실무적 1NF 최적화)
    options = models.JSONField(verbose_name="선택지(배열)") 
    answer = models.CharField(max_length=100, verbose_name="정답")
    explanation = models.TextField(verbose_name="해설")

    class Meta:
        db_table = 'quiz'
        verbose_name = '퀴즈'
        verbose_name_plural = '퀴즈 목록'

    def __str__(self):
        return self.question[:20]


class UserQuizHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_histories', verbose_name="사용자")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='histories', verbose_name="퀴즈")
    is_correct = models.BooleanField(verbose_name="정답 여부")
    user_choice = models.CharField(max_length=100, blank=True, default='', verbose_name="사용자 선택")
    solved_at = models.DateTimeField(auto_now_add=True, verbose_name="풀이 일시")
    solved_date = models.DateField(verbose_name="풀이 일자")

    class Meta:
        db_table = 'user_quiz_history'
        verbose_name = '사용자 퀴즈 풀이 이력'
        verbose_name_plural = '사용자 퀴즈 풀이 이력 목록'
        unique_together = ('user', 'solved_date')  # 사용자당 하루 1건만 기록

    def __str__(self):
        return f"{self.user.username} - 퀴즈 {self.quiz.id} ({'정답' if self.is_correct else '오답'})"
    
# 기존 모델들은 그대로 유지하고 아래 코드만 추가
class UserTermReadHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_terms')
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_term_read_history'
        unique_together = ('user', 'term') # 동일한 용어를 여러 번 읽어도 한 번만 기록

    def __str__(self):
        return f"{self.user.username} - {self.term.term_name} 읽음"