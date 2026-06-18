"""대상 시장지수들의 등락률 평균으로 '투자 날씨'를 산출한다.

상승일수록 긍정(맑음), 하락일수록 부정(폭풍). 임계값은 아래 상수로 조정 가능.
대상 지수는 index_collector.TARGET_INDICES(코스피·코스닥·코스피200·KRX300).
"""

from django.utils import timezone

from .models import MarketIndexDaily, DailyMarketWeather
from .index_collector import TARGET_INDICES

# combined(코스피·코스닥 평균 등락률, %) 구간별 (상태, 메시지).
# 큰 값(상승)부터 검사한다.
WEATHER_THRESHOLDS = [
	(1.5, DailyMarketWeather.WeatherStatus.SUNNY, "강세 마감 — 투자 심리가 좋은 날입니다."),
	(0.5, DailyMarketWeather.WeatherStatus.CLOUDY, "완만한 상승 흐름입니다."),
	(-0.5, DailyMarketWeather.WeatherStatus.RAINY, "약보합 — 관망세가 짙습니다."),
	(-1.5, DailyMarketWeather.WeatherStatus.SNOWY, "약세 — 변동성에 주의하세요."),
]
# 위 어느 구간에도 못 미치면(최저) STORMY.
WEATHER_FALLBACK = (DailyMarketWeather.WeatherStatus.STORMY, "큰 하락 — 변동성 경계가 필요합니다.")


def classify_weather(combined_rate):
	"""평균 등락률(%)을 5단계 (status, message)로 분류한다."""
	for lower_bound, bound_status, bound_message in WEATHER_THRESHOLDS:
		if combined_rate >= lower_bound:
			return bound_status, bound_message
	return WEATHER_FALLBACK


def compute_weather(index_rates):
	"""지수별 등락률(%) dict로 (status, message, indicator_data)를 산출한다.

	index_rates: dict[지수명 -> 등락률(float)]. 등락률 평균으로 날씨를 판단한다.
	"""
	rates = list(index_rates.values())
	combined = sum(rates) / len(rates) if rates else 0.0
	status, message = classify_weather(combined)

	indicator_data = {
		"combined_rate": round(combined, 2),
		"indices": {name: {"change_rate": rate} for name, rate in index_rates.items()},
	}
	return status, message, indicator_data


def store_today_weather():
	"""대상 지수들의 최신값을 읽어 오늘자 DailyMarketWeather를 산출·저장한다.

	반환: 저장된 DailyMarketWeather 인스턴스. 지수 데이터가 하나도 없으면 None.
	"""
	latest = {}
	for index_name in TARGET_INDICES:
		obj = MarketIndexDaily.objects.filter(index_name=index_name).first()
		if obj:
			latest[index_name] = obj
	if not latest:
		return None

	index_rates = {name: obj.change_rate for name, obj in latest.items()}
	status, message, indicator_data = compute_weather(index_rates)
	# 등락률 외에 종가도 함께 보관
	for name, obj in latest.items():
		indicator_data["indices"][name]["close_price"] = obj.close_price

	weather, _ = DailyMarketWeather.objects.update_or_create(
		target_date=timezone.localdate(),
		defaults={
			"weather_status": status,
			"message": message,
			"indicator_data": indicator_data,
		},
	)
	return weather
