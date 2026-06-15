"""순수 함수: 키워드 기반 섹터 분류 + 추천 섹터 선정.

DB/네트워크에 의존하지 않으므로 단위 테스트가 쉽다.
crawl_news 커맨드가 이 함수들을 사용한다.
"""


def classify_text(text, sector_keywords):
    """text(제목+요약)에 부분일치하는 섹터명 리스트를 반환한다.

    sector_keywords: dict[섹터명 -> list[str]].
    하나 이상의 키워드가 매칭되면 해당 섹터를 포함한다. 매칭 0개면 빈 리스트.
    """
    text_lower = text.lower()
    matched = []
    for name, keywords in sector_keywords.items():
        if any(str(kw).lower() in text_lower for kw in keywords):
            matched.append(name)
    return matched


def select_sectors(sector_counts, sector_scores=None, *, max_n=4, min_n=2, threshold=3):
    """추천 섹터를 순위 순으로 선정한다.

    sector_counts: dict[섹터명 -> int] (매칭된 기사 수). 0건 섹터는 넘기지 말 것.
    sector_scores: dict[섹터명 -> float] (최근성 가중 점수). 정렬 기준. 없으면 count로 정렬.
    규칙: 점수 내림차순으로 정렬 → 임계치(threshold) 이상인 섹터를 최대 max_n개 선정.
          단, 선정 결과가 min_n 미만이면 임계치 미달이어도 상위에서 min_n까지 채운다.
    반환: 섹터명 리스트 (최대 max_n개, rank 순). 후보가 부족하면 가능한 만큼만.
    """
    scores = sector_scores or sector_counts
    ranked = sorted(sector_counts, key=lambda n: scores[n], reverse=True)

    selected = [n for n in ranked if sector_counts[n] >= threshold][:max_n]

    if len(selected) < min_n:
        for name in ranked:
            if name not in selected:
                selected.append(name)
            if len(selected) >= min_n:
                break

    return selected[:max_n]
