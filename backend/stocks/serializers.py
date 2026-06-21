from rest_framework import serializers
from .models import Stock, StockPriceDaily, DailyMarketWeather, MarketIndexDaily, UserBookmark

class MarketIndexDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndexDaily
        fields = ['index_name', 'base_date', 'close_price', 'change', 'change_rate']

class DailyMarketWeatherSerializer(serializers.ModelSerializer):
    weather_emoji = serializers.SerializerMethodField()

    class Meta:
        model = DailyMarketWeather
        fields = ['target_date', 'weather_status', 'weather_emoji', 'message']

    def get_weather_emoji(self, obj):
        emoji_map = {
            'VERY_SUNNY': '☀️',
            'SUNNY': '🌤️',
            'CLOUDY': '☁️',
            'RAINY': '🌧️',
            'STORMY': '⛈️',
        }
        return emoji_map.get(obj.weather_status, '❓')
    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
    
class StockPriceDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPriceDaily
        fields = ['record_date', 'open_price', 'close_price', 'high_price', 'low_price', 'volume',]

class StockDetailSerializer(serializers.ModelSerializer):
    daily_prices = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ['id', 'stock_code', 'stock_name', 'market_type', 'daily_prices',]

    def get_daily_prices(self, obj):
        """최근 record_date 기준 상위 N건(기본 전체)을 오름차순으로 반환한다."""
        limit = self.context.get('price_limit')
        qs = obj.daily_prices.order_by('-record_date')
        if limit:
            qs = qs[:limit]
        prices = sorted(qs, key=lambda p: p.record_date)
        return StockPriceDailySerializer(prices, many=True).data


class UserBookmarkSerializer(serializers.ModelSerializer):
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    market_type = serializers.CharField(source='stock.market_type', read_only=True)

    class Meta:
        model = UserBookmark
        fields = ['id', 'stock_code', 'stock_name', 'market_type', 'created_at']


