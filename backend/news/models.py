from django.db import models


class Sector(models.Model):
    """고정 섹터 분류표. keywords 부분일치로 기사를 섹터에 매칭한다."""
    name = models.CharField(max_length=100, unique=True)
    keywords = models.JSONField(default=list)  # list[str]
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


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
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=500, unique=True)  # 중복 방지 키
    summary_raw = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField(db_index=True)
    content_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
