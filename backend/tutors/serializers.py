from rest_framework import serializers
from .models import Term, DailyTerm, Quiz, UserQuizHistory

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'

class DailyTermSerializer(serializers.ModelSerializer):
    term = TermSerializer(read_only=True) # 연결된 용어의 상세 정보까지 한 번에 반환

    class Meta:
        model = DailyTerm
        fields = ['id', 'date', 'term']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        # 정답(answer)/해설(explanation)은 노출하지 않는다.
        # 채점은 QuizViewSet의 check 액션(서버 채점)으로 처리한다.
        fields = ['id', 'question', 'options']

class UserQuizHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizHistory
        fields = ['id', 'user', 'quiz', 'is_correct', 'solved_at']
        read_only_fields = ['user']