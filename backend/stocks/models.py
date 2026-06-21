from django.db import models
from django.conf import settings    # 모델 참조를 위해 필요

# Create your models here.

class Stock(models.Model):
    stock_code = models.CharField(max_length=20, unique=True, db_index=True)
    stock_name = models.CharField(max_length=100)
    market_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.stock_name} ({self.stock_code})"

class StockPriceDaily(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='daily_prices')
    record_date = models.DateField(db_index=True)
    open_price = models.IntegerField()
    close_price = models.IntegerField()
    high_price = models.IntegerField()
    low_price = models.IntegerField()
    volume = models.BigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stock', 'record_date'], name='unique_stock_date_price')
        ]

class DailyMarketWeather(models.Model):
    class WeatherStatus(models.TextChoices):
        VERY_SUNNY = 'VERY_SUNNY', '매우맑음'
        SUNNY = 'SUNNY', '맑음'
        CLOUDY = 'CLOUDY', '흐림'
        RAINY = 'RAINY', '비'
        STORMY = 'STORMY', '비+천둥'
    
    target_date = models.DateField(unique=True, db_index=True)
    weather_status = models.CharField(
        max_length=20,
        choices=WeatherStatus.choices,
        default=WeatherStatus.SUNNY,
    )
    message = models.TextField()
    indicator_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class MarketIndexDaily(models.Model):
    """코스피·코스닥 등 시장 지수의 일별 종가/등락. 개별 종목 시세(StockPriceDaily)와 별개 데이터."""
    index_name = models.CharField(max_length=20, db_index=True)  # 코스피, 코스닥
    base_date = models.DateField(db_index=True)
    close_price = models.FloatField()       # clpr (종가 지수)
    change = models.FloatField()            # vs (전일 대비)
    change_rate = models.FloatField()       # fltRt (등락률 %)

    class Meta:
        ordering = ['-base_date']
        constraints = [
            models.UniqueConstraint(fields=['index_name', 'base_date'], name='uniq_index_date')
        ]

    def __str__(self):
        return f"{self.base_date} {self.index_name} {self.close_price} ({self.change_rate:+.2f}%)"


class TrendKeyword(models.Model):
    target_date = models.DateField(db_index=True)
    keyword_name = models.CharField(max_length=100)
    tf_idf_score = models.FloatField()

class StockKeyWordMapping(models.Model):
    keyword = models.ForeignKey(TrendKeyword, on_delete=models.CASCADE, related_name='stock_mappings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='keyword_mappings')

class UserBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'stock'], name='unique_user_bookmark'),
        ]









