import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from . import views


@pytest.fixture
def api_client():
	return APIClient()


class TestChatbotAPI:
	def test_health_ok(self, api_client):
		response = api_client.get(reverse('chatbot:health'))
		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == 'ok'

	def test_empty_message_rejected(self, api_client):
		response = api_client.post(reverse('chatbot:chat'), {'message': '   '}, format='json')
		assert response.status_code == status.HTTP_400_BAD_REQUEST

	def test_guardrail_pass_returns_reply(self, api_client, monkeypatch):
		"""가드레일 통과 시 GMS 응답(reply)을 반환한다."""
		monkeypatch.setattr(views, 'check_guardrail', lambda prompt: {'result': True, 'reason': 'ok'})
		monkeypatch.setattr(views, 'chat_completion', lambda history: '삼성전자는 코스피 대표 종목입니다.')

		response = api_client.post(reverse('chatbot:chat'), {'message': '삼성전자 어때?'}, format='json')
		assert response.status_code == status.HTTP_200_OK
		assert response.data['allowed'] is True
		assert response.data['reply'] == '삼성전자는 코스피 대표 종목입니다.'

	def test_guardrail_block_returns_refusal(self, api_client, monkeypatch):
		"""가드레일에 걸리면 chat_completion 을 호출하지 않고 거절 문구를 반환한다."""
		called = {'chat': False}

		def _chat(history):
			called['chat'] = True
			return 'should not be called'

		monkeypatch.setattr(views, 'check_guardrail', lambda prompt: {'result': False, 'reason': '부적절'})
		monkeypatch.setattr(views, 'chat_completion', _chat)

		response = api_client.post(reverse('chatbot:chat'), {'message': '나쁜 질문'}, format='json')
		assert response.status_code == status.HTTP_200_OK
		assert response.data['allowed'] is False
		assert called['chat'] is False
		assert '주식' in response.data['reply']

	def test_gms_error_returns_502(self, api_client, monkeypatch):
		def _raise(prompt):
			raise views.GmsError('connection failed')

		monkeypatch.setattr(views, 'check_guardrail', _raise)
		response = api_client.post(reverse('chatbot:chat'), {'message': '질문'}, format='json')
		assert response.status_code == status.HTTP_502_BAD_GATEWAY
