import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import UserFactory

@pytest.mark.django_db
class TestAdvancedAccountsAPI:
    def test_profile_image_upload(self, api_client):
        """
        TODO: 프로필 이미지 업로드 기능 구현 시 테스트
        - 회원가입 시 이미지 등록
        - 회원정보 수정 시 이미지 수정
        """
        pytest.skip("프로필 이미지 업로드 기능 개발 후 테스트 로직 작성")

    def test_password_change(self, api_client):
        """
        TODO: 비밀번호 변경/확인 기능 구현 시 테스트
        - 회원정보 수정 페이지에서 비밀번호 변경 가능 여부
        - 2차 비밀번호 확인 절차 검증
        """
        pytest.skip("비밀번호 변경 기능 개발 후 테스트 로직 작성")
