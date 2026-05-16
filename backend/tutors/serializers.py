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
        # 정답(answer)과 해설(explanation)을 리스트 조회에서는 숨길지 판단해야 함
        # 현재는 통째로 넘겨주고 Vue에서 정답 확인 후 해설을 띄우는 구조를 가정
        fields = '__all__' 

class UserQuizHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuizHistory
        fields = ['id', 'user', 'quiz', 'is_correct', 'solved_at']
        read_only_fields = ['user']