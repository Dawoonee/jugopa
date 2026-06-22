from django.db import models


class Sector(models.Model):
    """WICS 기반 섹터 분류표(자기참조 계층).

    - level=LARGE: 대분류 10개(관심 섹터 선택 단위, parent=None)
    - level=MID: 중분류 28개(기사/카드뉴스 분류 단위, parent=대분류)
    keywords(중분류에만 부여)를 기사 제목+요약에 부분일치시켜 섹터를 매칭한다.
    """

    class Level(models.TextChoices):
        LARGE = 'LARGE', '대분류'
        MID = 'MID', '중분류'

    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.MID)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='children'
    )
    keywords = models.JSONField(default=list)  # list[str] (중분류에서만 사용)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'level'], name='uniq_sector_name_level')
        ]

    def __str__(self):
        return f"[{self.level}] {self.name}"


class SectorStock(models.Model):
    """섹터(업종) ↔ 대표 종목 매핑. 추천 섹터 카드의 TOP 종목 게이지에 사용된다."""
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='sector_stocks')
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE, related_name='sector_links')
    rank = models.IntegerField(default=0)  # 섹터 내 순위 (0이 최상위)

    class Meta:
        ordering = ['sector', 'rank']
        constraints = [
            models.UniqueConstraint(fields=['sector', 'stock'], name='uniq_sector_stock')
        ]

    def __str__(self):
        return f"{self.sector.name} #{self.rank} {self.stock.stock_name}"


class NewsArticle(models.Model):
    """RSS로 수집한 원문 기사."""

    class Sentiment(models.TextChoices):
        POSITIVE = '긍정', '긍정'
        NEGATIVE = '부정', '부정'
        UNANALYZED = '미분석', '미분석'

    title = models.CharField(max_length=500)
    link = models.URLField(max_length=500, unique=True)  # 중복 방지 키
    summary_raw = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField(db_index=True)
    content_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(  # KR-FinBert-SC 감성 분석 결과
        max_length=10, choices=Sentiment.choices,
        default=Sentiment.UNANALYZED, db_index=True,
    )

    sectors = models.ManyToManyField(Sector, related_name='articles', blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"[{self.source}] {self.title}"


class SectorCardNews(models.Model):
    """LLM이 정리한 추천 섹터 카드뉴스(일자별 1건)."""
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='card_news')
    target_date = models.DateField(db_index=True)
    headline = models.CharField(max_length=255)  # 한줄요약
    summary = models.TextField()  # 카드 본문
    key_points = models.JSONField(default=list)  # list[str]
    article_count = models.IntegerField(default=0)
    representative_articles = models.ManyToManyField(
        NewsArticle, related_name='featured_in', blank=True
    )
    rank = models.IntegerField(default=0)  # 추천 순위 (1이 최상위)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date', 'rank']
        constraints = [
            models.UniqueConstraint(fields=['sector', 'target_date'], name='uniq_sector_date')
        ]

    def __str__(self):
        return f"{self.target_date} #{self.rank} {self.sector.name}"
