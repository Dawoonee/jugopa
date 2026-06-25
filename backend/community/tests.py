import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import CommunityPost, CommunityComment
from stocks.models import Stock

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="testpassword123", nickname="tester")

@pytest.fixture
def other_user():
    return User.objects.create_user(username="otheruser", password="testpassword123", nickname="other")

@pytest.fixture
def test_stock():
    return Stock.objects.create(stock_code="005930", stock_name="삼성전자", market_type="KOSPI")

@pytest.fixture
def test_post(test_user, test_stock):
    return CommunityPost.objects.create(
        user=test_user,
        stock=test_stock,
        title="Test Post",
        content="This is a test post content"
    )

@pytest.fixture
def test_comment(test_user, test_post):
    return CommunityComment.objects.create(
        user=test_user,
        post=test_post,
        content="Test comment"
    )

@pytest.mark.django_db
class TestCommunityAPI:
    def test_post_list(self, api_client, test_post):
        url = reverse('community:communitypost-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_post_create(self, api_client, test_user, test_stock):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitypost-list')
        data = {
            "title": "New Post",
            "content": "New Content",
            "stock": test_stock.id
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert CommunityPost.objects.filter(title="New Post").exists()

    def test_post_update_owner(self, api_client, test_user, test_post):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitypost-detail', kwargs={'pk': test_post.id})
        data = {"title": "Updated Title"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_post.refresh_from_db()
        assert test_post.title == "Updated Title"

    def test_post_update_not_owner(self, api_client, other_user, test_post):
        api_client.force_authenticate(user=other_user)
        url = reverse('community:communitypost-detail', kwargs={'pk': test_post.id})
        data = {"title": "Hacked Title"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_post_delete_owner(self, api_client, test_user, test_post):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitypost-detail', kwargs={'pk': test_post.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CommunityPost.objects.filter(id=test_post.id).exists()

    def test_post_delete_not_owner(self, api_client, other_user, test_post):
        api_client.force_authenticate(user=other_user)
        url = reverse('community:communitypost-detail', kwargs={'pk': test_post.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert CommunityPost.objects.filter(id=test_post.id).exists()

    def test_post_like(self, api_client, test_user, test_post):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitypost-like', kwargs={'pk': test_post.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['liked'] is True
        assert response.data['like_count'] == 1

        # Like toggle
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['liked'] is False
        assert response.data['like_count'] == 0

    def test_comment_list_by_post(self, api_client, test_comment, test_post):
        url = reverse('community:communitycomment-list')
        response = api_client.get(f'{url}?post={test_post.id}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_comment_create(self, api_client, test_user, test_post):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitycomment-list')
        data = {
            "post": test_post.id,
            "content": "New Comment"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert CommunityComment.objects.filter(content="New Comment").exists()

    def test_comment_like(self, api_client, test_user, test_comment):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitycomment-like', kwargs={'pk': test_comment.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['liked'] is True

    def test_comment_update_owner(self, api_client, test_user, test_comment):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitycomment-detail', kwargs={'pk': test_comment.id})
        data = {"content": "Updated Comment"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_comment.refresh_from_db()
        assert test_comment.content == "Updated Comment"

    def test_comment_update_not_owner(self, api_client, other_user, test_comment):
        api_client.force_authenticate(user=other_user)
        url = reverse('community:communitycomment-detail', kwargs={'pk': test_comment.id})
        data = {"content": "Hacked Comment"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_comment_delete_owner(self, api_client, test_user, test_comment):
        api_client.force_authenticate(user=test_user)
        url = reverse('community:communitycomment-detail', kwargs={'pk': test_comment.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CommunityComment.objects.filter(id=test_comment.id).exists()

    def test_comment_delete_not_owner(self, api_client, other_user, test_comment):
        api_client.force_authenticate(user=other_user)
        url = reverse('community:communitycomment-detail', kwargs={'pk': test_comment.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert CommunityComment.objects.filter(id=test_comment.id).exists()
