"""감성 분석 결과를 활용한 추천 섹터 선정 서비스."""

from news.models import NewsArticle, Sector
from news.sentiment import analyze_articles_by_sector

TOP_N = 3


def get_top3_positive_sectors():
    """긍정 기사가 가장 많은 상위 3개 업종을 반환한다.

    반환: [(Sector, [긍정 NewsArticle, ...]), ...] — 긍정 기사 수 내림차순, 최대 3개.
          긍정 기사가 0건인 섹터는 제외된다.
    """
    active_mid_ids = Sector.objects.filter(
        level=Sector.Level.MID, is_active=True
    ).values_list('id', flat=True)

    positive_articles = (
        NewsArticle.objects
        .filter(
            sentiment=NewsArticle.Sentiment.POSITIVE,
            sectors__in=active_mid_ids,
        )
        .distinct()
        .prefetch_related('sectors')
    )

    grouped = analyze_articles_by_sector(positive_articles)
    return grouped[:TOP_N]
