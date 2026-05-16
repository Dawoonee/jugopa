from rest_framework import serializers
from .models import Stock, StockPriceDaily, DailyMarketWeather

class DailyMarketWeatherSerializer(serializers.ModelSerializer):
    weather_emoji = serializers.SerializerMethodField()

    class Meta:
        model = DailyMarketWeather
        fields = ['target_date', 'weather_status', 'weather_emoji', 'message']

    def get_weather_emoji(self, obj):
        emoji_map = {
            'SUNNY': '☀️',
            'CLOUDY': '☁️',
            'RAINY': '🌧️',
            'SNOWY': '❄️',
            'STORMY': '⚡',
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
    daily_prices = StockPriceDailySerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'stock_code', 'stock_name', 'market_type', 'daily_prices',]


