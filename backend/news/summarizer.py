"""GMS(OpenAI 호환 API)로 섹터별 기사를 한줄요약 + 카드뉴스로 정리한다.

/chat/completions 의 구조화 출력(response_format=json_schema)을 사용한다.
GMS_API_KEY2 / GMS_BASE_URL2 / GMS_MODEL2 는 settings(.env)에서 읽는다(챗봇과 별도 키).
반환은 기존과 동일한 SectorCard(headline/summary/key_points) 인스턴스라 호출부 변경이 없다.
"""

import json

import requests
from django.conf import settings
from pydantic import BaseModel

# 카드 요약 호출 타임아웃(초). gpt-5-nano는 추론 시간이 있어 응답 타임아웃을 넉넉히 둔다.
REQUEST_TIMEOUT = (5, 120)

SYSTEM_PROMPT = "너는 한국 경제 뉴스를 주식 입문자가 이해하기 쉽게 요약하는 에디터다."

# 카드뉴스 구조화 출력 스키마.
RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "sector_card",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "headline": {"type": "string", "description": "한 문장 요약"},
                "summary": {"type": "string", "description": "2~3문장 카드 본문"},
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "핵심 이슈 3개",
                },
            },
            "required": ["headline", "summary", "key_points"],
            "additionalProperties": False,
        },
    },
}


class SectorCard(BaseModel):
    headline: str           # 한줄요약
    summary: str            # 2~3문장 카드 본문
    key_points: list[str]   # 핵심 이슈 불릿 3개


def summarize_sector(sector_name, articles):
    """한 섹터의 기사 목록을 카드뉴스용으로 요약한다.

    articles: list[dict] — 각 항목은 {"title": str, "summary": str}.
    반환: SectorCard (검증된 Pydantic 인스턴스).
    GMS 호출/파싱 오류는 호출자(generate_positive_cardnews)가 처리하도록 그대로 전파한다.
    """
    if not settings.GMS_API_KEY2 or not settings.GMS_BASE_URL2:
        raise RuntimeError("GMS_API_KEY2 / GMS_BASE_URL2 가 설정되지 않았습니다.")

    joined = "\n".join(f"- {a['title']}: {a['summary']}" for a in articles)
    user_content = (
        f"다음은 '{sector_name}' 섹터 관련 최근 기사 목록이다. "
        f"이 섹터에서 일어난 핵심 이슈를 카드뉴스용으로 정리하라. "
        f"headline은 한 문장 요약, summary는 2~3문장, key_points는 핵심 이슈 3개로 작성하라."
        f"\n\n{joined}"
    )
    payload = {
        "model": settings.GMS_MODEL2,
        "messages": [
            {"role": "developer", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "response_format": RESPONSE_FORMAT,
    }
    url = f"{settings.GMS_BASE_URL2}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GMS_API_KEY2}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return SectorCard(**json.loads(content))
