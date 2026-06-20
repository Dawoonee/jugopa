import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username="testuser",
        password="testpassword123",
        nickname="tester"
    )

@pytest.mark.django_db
class TestAccountsAPI:
    def test_signup(self, api_client):
        url = reverse('accounts:signup')
        data = {
            "username": "newuser",
            "password": "securepassword123",
            "nickname": "newbie"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()

    def test_random_password(self, api_client):
        url = reverse('accounts:random_password')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "recommended_password" in response.data

    def test_login(self, api_client, test_user):
        url = reverse('accounts:login')
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_profile_get_unauthenticated(self, api_client):
        url = reverse('accounts:profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_get_authenticated(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == "testuser"

    def test_profile_update(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile')
        data = {"nickname": "updated_tester"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.nickname == "updated_tester"

    def test_profile_delete(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile')
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=test_user.id).exists()

    def test_profile_stats(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile_stats')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bookmark_count'] == 0
        assert response.data['quiz_count'] == 0
        assert response.data['today_visited'] is True
        assert response.data['first_visit_today'] is True
        
        # Second visit should return first_visit_today=False
        response = api_client.get(url)
        assert response.data['first_visit_today'] is False

    def test_quiz_calendar(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:quiz_calendar')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'total_solved' in response.data
        assert 'current_streak' in response.data
        assert 'longest_streak' in response.data
        assert 'daily' in response.data
