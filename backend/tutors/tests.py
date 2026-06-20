import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Term, DailyTerm, Quiz, UserQuizHistory, UserTermReadHistory

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="testpassword123", nickname="tester")

@pytest.fixture
def test_term():
    return Term.objects.create(term_name="PER", explanation="주가수익비율")

@pytest.fixture
def test_daily_term(test_term):
    today = timezone.localdate()
    return DailyTerm.objects.create(date=today, term=test_term)

@pytest.fixture
def test_quiz():
    return Quiz.objects.create(
        question="다음 중 PER의 올바른 설명은?",
        options=["주가수익비율", "주당순이익", "자기자본이익률"],
        answer="주가수익비율",
        explanation="PER은 주가수익비율입니다."
    )

@pytest.mark.django_db
class TestTutorsAPI:
    def test_terms_list(self, api_client, test_term):
        url = reverse('tutors:term-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_daily_terms_list(self, api_client, test_daily_term):
        url = reverse('tutors:dailyterm-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_daily_term_today(self, api_client, test_term):
        url = reverse('tutors:dailyterm-today')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['term']['term_name'] == "PER"

    def test_daily_term_read(self, api_client, test_user, test_daily_term):
        api_client.force_authenticate(user=test_user)
        url = reverse('tutors:dailyterm-read', kwargs={'pk': test_daily_term.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert UserTermReadHistory.objects.filter(user=test_user, term=test_daily_term.term).exists()

    def test_quizzes_list(self, api_client, test_quiz):
        url = reverse('tutors:quiz-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_quiz_check_correct(self, api_client, test_user, test_quiz):
        api_client.force_authenticate(user=test_user)
        url = reverse('tutors:quiz-check', kwargs={'pk': test_quiz.id})
        data = {"answer": "주가수익비율"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is True
        assert UserQuizHistory.objects.filter(user=test_user, quiz=test_quiz, is_correct=True).exists()

    def test_quiz_check_incorrect(self, api_client, test_user, test_quiz):
        api_client.force_authenticate(user=test_user)
        url = reverse('tutors:quiz-check', kwargs={'pk': test_quiz.id})
        data = {"answer": "오답"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is False
        assert UserQuizHistory.objects.filter(user=test_user, quiz=test_quiz, is_correct=False).exists()

    def test_quiz_history_list(self, api_client, test_user, test_quiz):
        api_client.force_authenticate(user=test_user)
        UserQuizHistory.objects.create(user=test_user, quiz=test_quiz, is_correct=True)
        url = reverse('tutors:quiz-history-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_review_quiz_questions(self, api_client, test_user, test_term):
        api_client.force_authenticate(user=test_user)
        UserTermReadHistory.objects.create(user=test_user, term=test_term)
        url = reverse('tutors:review-quiz-questions')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['term_id'] == test_term.id

    def test_review_quiz_submit_correct(self, api_client, test_user, test_term):
        api_client.force_authenticate(user=test_user)
        url = reverse('tutors:review-quiz-submit')
        data = {"term_id": test_term.id, "answer": "PER"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is True

    def test_review_quiz_submit_incorrect(self, api_client, test_user, test_term):
        api_client.force_authenticate(user=test_user)
        url = reverse('tutors:review-quiz-submit')
        data = {"term_id": test_term.id, "answer": "WRONG"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_correct'] is False
