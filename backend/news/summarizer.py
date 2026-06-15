"""Claude API로 섹터별 기사를 한줄요약 + 카드뉴스로 정리한다.

Anthropic SDK의 구조화 출력(messages.parse + Pydantic)을 사용한다.
ANTHROPIC_API_KEY는 환경변수에서 자동으로 읽는다(settings의 read_env가 .env를 os.environ에 로드).
"""

import anthropic
from pydantic import BaseModel

# 기본 모델. 다건 배치라 비용이 우선이면 "claude-sonnet-4-6"으로 교체 가능.
MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = "너는 한국 경제 뉴스를 주식 입문자가 이해하기 쉽게 요약하는 에디터다."


class SectorCard(BaseModel):
    headline: str           # 한줄요약
    summary: str            # 2~3문장 카드 본문
    key_points: list[str]   # 핵심 이슈 불릿 3개


def summarize_sector(sector_name, articles):
    """한 섹터의 기사 목록을 카드뉴스용으로 요약한다.

    articles: list[dict] — 각 항목은 {"title": str, "summary": str}.
    반환: SectorCard (검증된 Pydantic 인스턴스).
    Anthropic API 오류는 호출자(crawl_news)가 처리하도록 그대로 전파한다.
    """
    client = anthropic.Anthropic()
    joined = "\n".join(f"- {a['title']}: {a['summary']}" for a in articles)
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"다음은 '{sector_name}' 섹터 관련 최근 기사 목록이다. "
                f"이 섹터에서 일어난 핵심 이슈를 카드뉴스용으로 정리하라. "
                f"headline은 한 문장 요약, summary는 2~3문장, key_points는 핵심 이슈 3개로 작성하라."
                f"\n\n{joined}"
            ),
        }],
        output_format=SectorCard,
    )
    return resp.parsed_output
