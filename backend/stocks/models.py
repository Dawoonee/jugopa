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
        SUNNY = 'SUNNY', '맑음'
        CLOUDY = 'CLOUDY', '흐림'
        RAINY = 'RAINY', '비'
        SNOWY = 'SNOWY', '눈'
        STORMY = 'STORMY', '폭풍'
    
    target_date = models.DateField(unique=True, db_index=True)
    weather_status = models.CharField(
        max_length=20,
        choices=WeatherStatus.choices,
        default=WeatherStatus.SUNNY,
    )
    message = models.TextField()
    indicator_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class TrendKeyword(models.Model):
    target_date = models.DateField(db_index=True)
    weather_status = models.CharField(max_length=50)
    message = models.TextField()
    indicator_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

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









