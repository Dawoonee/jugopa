import hashlib
from datetime import datetime, timedelta, timezone as dt_timezone

import feedparser
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.utils import timezone

from news.feeds import FEEDS, RECENT_DAYS
from news.models import Sector, NewsArticle, SectorCardNews
from news.selection import classify_text, select_sectors
from news import summarizer

# LLM 프롬프트에 넣을 섹터당 최대 기사 수 (프롬프트 비대화 방지).
MAX_ARTICLES_PER_PROMPT = 15
# 카드에 연결할 대표 기사 수.
MAX_REPRESENTATIVE = 3


class Command(BaseCommand):
    help = 'RSS로 경제 뉴스를 수집·분류하고, 추천 섹터를 Claude로 요약해 카드뉴스를 저장합니다.'

    def handle(self, *args, **options):
        sectors = list(Sector.objects.filter(level=Sector.Level.MID, is_active=True))
        if not sectors:
            self.stdout.write(self.style.ERROR(
                "활성 중분류 섹터가 없습니다. 먼저 `python manage.py load_sectors`를 실행하세요."
            ))
            return

        cutoff = timezone.now() - timedelta(days=RECENT_DAYS)

        entries = self._collect_entries()
        saved = self._upsert_articles(entries, cutoff)
        self.stdout.write(f"수집/저장된 최근 {RECENT_DAYS}일 기사: {len(saved)}건")

        sector_articles = self._classify(saved, sectors)
        selected = self._select(sector_articles)
        self.stdout.write(
            "선정 섹터: " + (", ".join(selected) if selected else "(없음)")
        )

        created = self._build_cards(selected, sector_articles)
        self.stdout.write(self.style.SUCCESS(
            f"카드뉴스 {created}건 생성/갱신 완료 (target_date={timezone.localdate()})."
        ))

    # --- 1. RSS 수집 -----------------------------------------------------
    def _collect_entries(self):
        entries = []
        for source, url in FEEDS:
            try:
                parsed = feedparser.parse(url)
            except Exception as exc:  # 네트워크/파싱 실패 피드는 건너뜀
                self.stdout.write(self.style.WARNING(f"  - {source} 파싱 실패: {exc}"))
                continue
            if parsed.bozo and not parsed.entries:
                self.stdout.write(self.style.WARNING(f"  - {source} 피드를 읽지 못했습니다."))
                continue
            for entry in parsed.entries:
                article = self._to_article(entry, source)
                if article:
                    entries.append(article)
        return entries

    def _to_article(self, entry, source):
        link = entry.get('link')
        title = entry.get('title')
        if not link or not title:
            return None
        summary_raw = _clean_html(entry.get('summary', ''))
        published_at = _to_datetime(entry.get('published_parsed'))
        content_hash = hashlib.sha256(
            f"{title}{summary_raw}".encode('utf-8')
        ).hexdigest()
        return {
            'title': title.strip()[:500],
            'link': link.strip()[:500],
            'summary_raw': summary_raw,
            'source': source,
            'published_at': published_at,
            'content_hash': content_hash,
        }

    # --- 2. 저장·중복제거 ------------------------------------------------
    def _upsert_articles(self, entries, cutoff):
        saved = []
        seen_links = set()  # 같은 실행 내 중복 링크(여러 피드 중복 게재) 제거
        for data in entries:
            if data['published_at'] < cutoff:
                continue
            link = data.pop('link')
            if link in seen_links:
                continue
            seen_links.add(link)
            article, _ = NewsArticle.objects.update_or_create(
                link=link, defaults=data,
            )
            saved.append(article)
        return saved

    # --- 3. 섹터 분류 ----------------------------------------------------
    def _classify(self, articles, sectors):
        keyword_map = {s.name: s.keywords for s in sectors}
        sector_by_name = {s.name: s for s in sectors}
        sector_articles = {s.name: [] for s in sectors}

        for article in articles:
            text = f"{article.title} {article.summary_raw}"
            matched = classify_text(text, keyword_map)
            if not matched:
                continue
            article.sectors.set([sector_by_name[name] for name in matched])
            for name in matched:
                sector_articles[name].append(article)

        # 기사 0건 섹터는 후보에서 제외
        return {name: arts for name, arts in sector_articles.items() if arts}

    # --- 4. 추천 섹터 선정 ----------------------------------------------
    def _select(self, sector_articles):
        now = timezone.now()
        counts = {name: len(arts) for name, arts in sector_articles.items()}
        scores = {
            name: sum(_recency_weight(a.published_at, now) for a in arts)
            for name, arts in sector_articles.items()
        }
        return select_sectors(counts, scores)

    # --- 5. LLM 요약 + 카드 저장 ----------------------------------------
    def _build_cards(self, selected, sector_articles):
        today = timezone.localdate()
        created = 0
        for rank, name in enumerate(selected, start=1):
            articles = sorted(
                sector_articles[name], key=lambda a: a.published_at, reverse=True
            )
            payload = [
                {'title': a.title, 'summary': a.summary_raw}
                for a in articles[:MAX_ARTICLES_PER_PROMPT]
            ]
            try:
                card = summarizer.summarize_sector(name, payload)
            except Exception as exc:  # 실패 섹터는 건너뛰고 계속 진행
                self.stdout.write(self.style.WARNING(
                    f"  - '{name}' 요약 실패, 건너뜀: {exc}"
                ))
                continue

            sector = articles[0].sectors.get(name=name)
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


def _clean_html(text):
    """RSS description의 HTML 태그를 제거하고 텍스트만 반환한다."""
    if not text:
        return ''
    return BeautifulSoup(text, 'html.parser').get_text(separator=' ', strip=True)


def _to_datetime(published_parsed):
    """feedparser의 published_parsed(struct_time, UTC) → aware datetime.

    날짜가 없으면 현재 시각으로 대체한다.
    """
    if not published_parsed:
        return timezone.now()
    return datetime(*published_parsed[:6], tzinfo=dt_timezone.utc)


def _recency_weight(published_at, now):
    """최근일수록 높은 가중치. 하루 멀어질수록 감쇠한다."""
    age_days = max((now - published_at).total_seconds() / 86400.0, 0.0)
    return 1.0 / (1.0 + age_days)
