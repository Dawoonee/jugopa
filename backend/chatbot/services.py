"""GMS(OpenAI 호환 API)로 챗봇 가드레일·응답을 처리한다.

GMS_API_KEY / GMS_BASE_URL / GMS_MODEL 은 settings(.env)에서 읽는다.
HTTP 호출은 requests 를 사용하며, 모델/DB 는 필요 없다.
"""

import json

import requests
from django.conf import settings

# GMS 호출 타임아웃(초). 연결/응답 각각.
REQUEST_TIMEOUT = (5, 30)

GUARDRAIL_SYSTEM = """
	너는 질문 prompt 가 적절한지 판단하는 Guardrail 이다.
	질문이 적절한지 여부를 result 에 boolean 으로 응답하라.
	기준은 선정성과 법률 위배 가능성이다.
	그리고 그렇게 판단한 이유를 reason 에 기입하라.
"""

CHAT_SYSTEM = """
	너는 주식 투자 플랫폼 '주고파'의 친절한 도우미다.
	주식·경제·투자·금융 그리고 주고파 서비스 사용법에 대해서만 답한다.
	그 외 주제의 질문에는 정중히 답변 범위를 벗어났다고 안내하라.
	특정 종목 매수·매도 권유나 단정적인 수익 보장은 하지 말고,
	입문자도 이해하기 쉽게 핵심을 간결히 설명하라.
"""


class GmsError(Exception):
	"""GMS 호출 실패(네트워크/응답 파싱)를 나타낸다."""


def _headers():
	return {
		'Authorization': f'Bearer {settings.GMS_API_KEY}',
		'Content-Type': 'application/json',
	}


def _post_chat_completions(payload):
	"""GMS /chat/completions 를 호출하고 message content 문자열을 반환한다."""
	if not settings.GMS_API_KEY or not settings.GMS_BASE_URL:
		raise GmsError('GMS_API_KEY / GMS_BASE_URL 이 설정되지 않았습니다.')
	url = f'{settings.GMS_BASE_URL}/chat/completions'
	try:
		response = requests.post(url, headers=_headers(), json=payload, timeout=REQUEST_TIMEOUT)
		response.raise_for_status()
		return response.json()['choices'][0]['message']['content']
	except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
		raise GmsError(str(exc)) from exc


def check_guardrail(prompt):
	"""질문 prompt 의 적절성을 판단해 {'result': bool, 'reason': str} 을 반환한다."""
	messages = [
		{'role': 'developer', 'content': GUARDRAIL_SYSTEM},
		{'role': 'user', 'content': f'prompt: {prompt}'},
	]
	response_format = {
		'type': 'json_schema',
		'json_schema': {
			'name': 'guardrail_response',
			'strict': True,
			'schema': {
				'type': 'object',
				'properties': {
					'result': {
						'type': 'boolean',
						'description': '사용자의 prompt 가 적절한지 여부',
					},
					'reason': {
						'type': 'string',
						'description': 'result 가 도출된 이유',
					},
				},
				'required': ['result', 'reason'],
				'additionalProperties': False,
			},
		},
	}
	payload = {'model': settings.GMS_MODEL, 'messages': messages, 'response_format': response_format}
	content = _post_chat_completions(payload)
	try:
		result_dict = json.loads(content)
		return {'result': bool(result_dict['result']), 'reason': result_dict['reason']}
	except (json.JSONDecodeError, KeyError, TypeError) as exc:
		raise GmsError(f'가드레일 응답 파싱 실패: {exc}') from exc


def chat_completion(history):
	"""대화 history([{role, content}, ...]) 로 도메인 한정 답변 문자열을 반환한다."""
	messages = [{'role': 'developer', 'content': CHAT_SYSTEM}, *history]
	payload = {'model': settings.GMS_MODEL, 'messages': messages}
	return _post_chat_completions(payload)
