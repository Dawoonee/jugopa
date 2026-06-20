import pytest
from .factories import DailyTermFactory, QuizFactory

@pytest.mark.django_db
class TestAdvancedTutorsAPI:
    def test_quiz_daily_term_matching(self):
        """
        TODO: 오늘의 퀴즈와 오늘의 주식 단어가 매칭되는지 검증
        - 퀴즈 API 호출 시, 반환된 퀴즈가 해당 일자의 DailyTerm과 일치하는지 로직 확인
        """
        pytest.skip("오늘의 퀴즈-단어 매칭 기능 수정 후 테스트 로직 작성")
