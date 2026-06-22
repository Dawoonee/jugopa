"""GMS(OpenAI 호환 API)로 챗봇 가드레일·응답을 처리한다.

GMS_API_KEY / GMS_BASE_URL / GMS_MODEL 은 settings(.env)에서 읽는다.
HTTP 호출은 requests 를 사용하며, 모델/DB 는 필요 없다.
"""

import json
import os

import requests
from django.conf import settings

# GMS 호출 타임아웃(초). 연결/응답 각각.
REQUEST_TIMEOUT = (5, 30)

try:
	with open(os.path.join(settings.BASE_DIR, '../README.md'), 'r', encoding='utf-8') as f:
		JUGOPA_INFO = f.read()
except FileNotFoundError:
	JUGOPA_INFO = ""

GUARDRAIL_SYSTEM = """
	너는 질문 prompt 가 적절한지 판단하는 Guardrail 이다.
	질문이 적절한지 여부를 result 에 boolean 으로 응답하라.
	기준은 선정성과 법률 위배 가능성이다.
	그리고 그렇게 판단한 이유를 reason 에 기입하라.
"""

CHAT_SYSTEM = f"""
	너는 주식 투자 플랫폼 '주고파'의 친절한 도우미다.
	주식·경제·투자·금융 그리고 주고파 서비스 사용법에 대해서만 답한다.
	그 외 주제의 질문에는 정중히 답변 범위를 벗어났다고 안내하라.
	특정 종목 매수·매도 권유나 단정적인 수익 보장은 하지 말고,
	입문자도 이해하기 쉽게 핵심을 간결히 설명하라.

	[주고파 사이트 관련 지식]
	{JUGOPA_INFO}
	
	[제약 사항]
	1. 반드시 위 [주고파 사이트 관련 지식]을 바탕으로만 사이트에 대한 질문에 답변하라.
	2. 지식에 없는 내용이거나 불확실한 경우, 절대 지어내지 말고(Hallucination 금지) 알 수 없다고 답변하라.
	3. 사용자가 "주식을 사줘", "팔아줘" 처럼 명시적으로 거래를 요청한 경우에만 주고파가 교육 플랫폼이라 실제 거래가 불가능하다고 안내하고, 단순 차트 조회나 질문에는 불필요하게 거래 불가 사실을 언급하지 마라.
	4. 화면을 안내할 때 '/recommend' 같은 URL 경로를 절대 직접 노출하지 마라. 대신 "상단 네비게이션 바의 '주식 추천' 메뉴를 클릭하세요" 처럼 화면에 보이는 버튼이나 메뉴 이름으로 자연스럽게 안내하라.
	5. 답변이 너무 길어지지 않도록, 반드시 150자 이내로 핵심만 간결하게 답변하라.
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


_STOCK_CACHE = None

def get_stock_context(message):
	global _STOCK_CACHE
	if _STOCK_CACHE is None:
		try:
			from stocks.models import Stock
			_STOCK_CACHE = list(Stock.objects.all().values('stock_name', 'stock_code', 'market_type'))
		except Exception:
			return ""
	
	found = []
	for s in _STOCK_CACHE:
		# 종목명이 2글자 이상인 경우에만 매칭 (예: 'LG', 'SK' 등 너무 짧은 단어의 오탐지 최소화, 하지만 DB에 있는 명칭 정확히 매칭)
		if len(s['stock_name']) >= 2 and s['stock_name'] in message:
			found.append(f"- {s['stock_name']} (종목코드: {s['stock_code']}, 소속 시장: {s['market_type']})")
	
	if found:
		return "\n\n[사용자 질의 관련 주식 DB 검색 결과]\n아래는 사용자가 질문한 주식에 대해 DB에서 자동 검색된 정보입니다. 이 정보를 바탕으로 답변에 활용하세요.\n" + "\n".join(found)
	return ""

def chat_completion(history):
	"""대화 history([{role, content}, ...]) 로 도메인 한정 답변 문자열을 반환한다."""
	last_message = ""
	for h in reversed(history):
		if h.get('role') == 'user':
			last_message = h.get('content', '')
			break

	extra_context = get_stock_context(last_message)
	system_prompt = CHAT_SYSTEM + extra_context

	messages = [{'role': 'developer', 'content': system_prompt}, *history]
	payload = {
		'model': settings.GMS_MODEL, 
		'messages': messages,
	}
	return _post_chat_completions(payload)
