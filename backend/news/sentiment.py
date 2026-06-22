"""KR-FinBert-SC 기반 한국어 금융 뉴스 감성 분석.

HuggingFace `snunlp/KR-FinBert-SC` 모델을 싱글턴으로 1회만 로드한다(CPU 고정).
neutral 예측은 부정으로 취급한다(명백한 긍정만 '긍정').
"""

from news.models import NewsArticle

MODEL_NAME = "snunlp/KR-FinBert-SC"
MAX_LENGTH = 512

# 모듈 전역 캐시: 매 호출마다 모델을 재로드하지 않기 위한 싱글턴.
_PIPELINE = None


def _get_pipeline():
    """text-classification 파이프라인을 최초 1회만 생성해 반환한다(CPU)."""
    global _PIPELINE
    if _PIPELINE is None:
        # 무거운 의존성이라 모듈 import 시가 아니라 최초 사용 시에 로드한다.
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            pipeline,
        )

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _PIPELINE = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=-1,  # CPU 강제 (GPU 없는 환경 고려)
            truncation=True,
            max_length=MAX_LENGTH,
        )
    return _PIPELINE


def _label_to_sentiment(label):
    """모델 라벨 문자열을 '긍정'/'부정'으로 매핑한다.

    라벨 순서·개수에 의존하지 않도록 'pos' 포함 여부로 판정한다(neutral→부정).
    """
    if "pos" in str(label).lower():
        return NewsArticle.Sentiment.POSITIVE
    return NewsArticle.Sentiment.NEGATIVE


def analyze_sentiment(text):
    """단일 텍스트의 감성을 '긍정' 또는 '부정'으로 반환한다.

    빈 텍스트는 '미분석'으로 반환한다.
    """
    if not text or not text.strip():
        return NewsArticle.Sentiment.UNANALYZED
    result = _get_pipeline()(text[:MAX_LENGTH * 4])[0]  # 토크나이저가 다시 truncation
    return _label_to_sentiment(result["label"])


def analyze_articles_by_sector(articles_qs):
    """이미 sentiment가 채워진 기사들을 섹터별 긍정 기사로 묶어 반환한다.

    반환: [(Sector, [긍정 NewsArticle, ...]), ...] — 긍정 기사 수 내림차순.
          긍정 기사가 0건인 섹터는 제외한다.
    """
    by_sector = {}
    for article in articles_qs:
        if article.sentiment != NewsArticle.Sentiment.POSITIVE:
            continue
        for sector in article.sectors.all():
            by_sector.setdefault(sector.id, [sector, []])[1].append(article)

    grouped = [(sector, arts) for sector, arts in by_sector.values()]
    grouped.sort(key=lambda pair: len(pair[1]), reverse=True)
    return grouped
