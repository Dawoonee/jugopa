"""챗봇 API — 가드레일 통과 시에만 GMS 응답을 반환한다."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .services import GmsError, chat_completion, check_guardrail

# 가드레일에 걸린 질문에 대한 정중한 거절 문구.
REFUSAL_REPLY = '죄송해요, 그 질문에는 답변드리기 어려워요. 주식·투자 관련해서 물어봐 주세요!'


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
	"""프론트 '연결중' 상태 해제용 헬스 체크."""
	return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
	"""사용자 메시지를 가드레일로 거른 뒤, 통과하면 GMS 응답을 반환한다.

	body: {"message": str, "history": [{"role", "content"}, ...]}
	"""
	message = (request.data.get('message') or '').strip()
	if not message:
		return Response({'detail': 'message 가 비어 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

	history = request.data.get('history') or []
	try:
		guard = check_guardrail(message)
		if not guard['result']:
			return Response({'allowed': False, 'reason': guard['reason'], 'reply': REFUSAL_REPLY})
		reply = chat_completion([{'role': 'user', 'content': message}])
	except GmsError as exc:
		return Response({'detail': f'챗봇 연결에 실패했어요: {exc}'}, status=status.HTTP_502_BAD_GATEWAY)

	return Response({'allowed': True, 'reply': reply})
