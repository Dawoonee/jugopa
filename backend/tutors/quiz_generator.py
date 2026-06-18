"""Claude API로 금융 용어 1개를 '용어 → 뜻 4지선다' 퀴즈로 생성한다.

news/summarizer.py와 동일하게 Anthropic SDK의 구조화 출력(messages.parse + Pydantic)을 쓴다.
ANTHROPIC_API_KEY는 환경변수에서 자동으로 읽는다(settings의 read_env가 .env를 os.environ에 로드).
"""

import anthropic
from pydantic import BaseModel

# 대량 배치 생성이므로 비용·속도 우선으로 Sonnet 사용. 품질 우선이면 "claude-opus-4-8"으로 교체.
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = "너는 주식 입문자(주린이)를 위한 금융 용어 퀴즈를 출제하는 교육 에디터다."


class QuizItem(BaseModel):
	correct_choice: str         # 정답: 용어의 핵심 뜻을 1문장으로 요약
	distractors: list[str]      # 오답 3개: 그럴듯하지만 틀린 뜻 (정답과 혼동되기 쉬운 내용)


def generate_quiz_for_term(term_name, explanation):
	"""용어 1개에 대한 4지선다 퀴즈 항목을 생성한다.

	term_name: 용어명
	explanation: 사전 원문 설명(정답의 근거)
	반환: QuizItem (검증된 Pydantic 인스턴스).
	Anthropic API 오류는 호출자(generate_quizzes)가 처리하도록 그대로 전파한다.
	"""
	client = anthropic.Anthropic()
	resp = client.messages.parse(
		model=MODEL,
		max_tokens=1000,
		system=SYSTEM_PROMPT,
		messages=[{
			"role": "user",
			"content": (
				f"다음 금융 용어로 4지선다 퀴즈를 만들어라.\n"
				f"- 용어: {term_name}\n"
				f"- 사전 설명: {explanation}\n\n"
				f"correct_choice는 이 용어의 핵심 뜻을 한 문장으로 쉽게 요약하라.\n"
				f"distractors는 정답과 혼동되기 쉬운, 그럴듯하지만 틀린 뜻 3개를 각각 한 문장으로 작성하라.\n"
				f"모든 보기는 비슷한 길이와 문체로 작성해 정답이 티 나지 않게 하라."
			),
		}],
		output_format=QuizItem,
	)
	return resp.parsed_output
