"""감성 분석 기반 '긍정 카드뉴스' 파이프라인.

크롤링 → 섹터 분류 → KR-FinBert-SC 감성 분석 → 긍정 기사 TOP 3 업종 선정 →
각 업종을 기존 summarizer로 카드뉴스 생성, 까지를 한 커맨드로 실행한다.

크롤러(crawl_news)와 요약기(summarizer)는 수정 없이 재사용한다.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from news.feeds import RECENT_DAYS
from news.models import NewsArticle, Sector, SectorCardNews
from news.services import get_top3_positive_sectors
from news import sentiment, summarizer
from news.management.commands.crawl_news import (
    Command as CrawlCommand,
    MAX_ARTICLES_PER_PROMPT,
    MAX_REPRESENTATIVE,
)


class Command(BaseCommand):
    help = (
        'RSS 수집·섹터 분류 후 감성 분석을 수행하고, 긍정 기사가 가장 많은 '
        'TOP 3 업종의 카드뉴스를 생성합니다.'
    )

    def handle(self, *args, **options):
        sectors = list(Sector.objects.filter(level=Sector.Level.MID, is_active=True))
        if not sectors:
            self.stdout.write(self.style.ERROR(
                "활성 중분류 섹터가 없습니다. 먼저 `python manage.py load_sectors`를 실행하세요."
            ))
            return

        # 1. 기존 크롤러 재사용: 수집 → 저장 → 섹터 분류
        saved = self._crawl_and_classify(sectors)
        self.stdout.write(f"수집/저장된 최근 {RECENT_DAYS}일 기사: {len(saved)}건")

        # 2. 미분석 기사 감성 분석
        analyzed = self._run_sentiment()
        self.stdout.write(f"감성 분석 완료: {analyzed}건")

        # 3. 긍정 기사 TOP 3 업종 선정
        top3 = get_top3_positive_sectors()
        if not top3:
            self.stdout.write(self.style.WARNING("긍정 기사가 있는 업종이 없습니다."))
            return
        self.stdout.write("TOP 3 긍정 업종:")
        for rank, (sector, arts) in enumerate(top3, start=1):
            self.stdout.write(f"  {rank}. {sector.name} (긍정 {len(arts)}건)")

        # 4. 각 업종 카드뉴스 생성 (기존 summarizer 재사용)
        created = self._build_cards(top3)
        self.stdout.write(self.style.SUCCESS(
            f"카드뉴스 {created}건 생성/갱신 완료 (target_date={timezone.localdate()})."
        ))

    # --- 1. 크롤링 + 분류 (crawl_news 헬퍼 재사용) -----------------------
    def _crawl_and_classify(self, sectors):
        crawl = CrawlCommand()
        crawl.stdout = self.stdout
        crawl.style = self.style

        cutoff = timezone.now() - timedelta(days=RECENT_DAYS)
        entries = crawl._collect_entries()
        saved = crawl._upsert_articles(entries, cutoff)
        crawl._classify(saved, sectors)  # 기사에 sectors M2M 설정
        return saved

    # --- 2. 감성 분석 ----------------------------------------------------
    def _run_sentiment(self):
        unanalyzed = NewsArticle.objects.filter(
            sentiment=NewsArticle.Sentiment.UNANALYZED
        )
        count = 0
        for article in unanalyzed.iterator():
            text = f"{article.title} {article.summary_raw}"
            article.sentiment = sentiment.analyze_sentiment(text)
            article.save(update_fields=['sentiment'])
            count += 1
        return count

    # --- 4. 카드뉴스 생성 (summarizer 그대로 호출) ----------------------
    def _build_cards(self, top3):
        today = timezone.localdate()
        created = 0
        for rank, (sector, positive_articles) in enumerate(top3, start=1):
            articles = sorted(
                positive_articles, key=lambda a: a.published_at, reverse=True
            )
            payload = [
                {'title': a.title, 'summary': a.summary_raw}
                for a in articles[:MAX_ARTICLES_PER_PROMPT]
            ]
            try:
                card = summarizer.summarize_sector(sector.name, payload)
            except Exception as exc:  # 실패 섹터는 건너뛰고 계속 진행
                self.stdout.write(self.style.WARNING(
                    f"  - '{sector.name}' 요약 실패, 건너뜀: {exc}"
                ))
                continue

            obj, _ = SectorCardNews.objects.update_or_create(
                sector=sector,
                target_date=today,
                defaults={
                    'headline': card.headline,
                    'summary': card.summary,
                    'key_points': card.key_points,
                    'article_count': len(articles),
                    'rank': rank,
                },
            )
            obj.representative_articles.set(articles[:MAX_REPRESENTATIVE])
            created += 1
        return created
