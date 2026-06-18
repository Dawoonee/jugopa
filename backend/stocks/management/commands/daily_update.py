"""홈 대시보드용 일배치: 지수 수집 → 투자 날씨 산출 → 뉴스 섹터 갱신.

n8n/cron이 매일 10:30(KST)에 `python manage.py daily_update`로 호출하는 것을 전제로 한다.
각 단계는 독립적으로 try/except 처리해 한 단계가 실패해도 다음 단계를 계속 진행한다.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from stocks.index_collector import collect_indices
from stocks.weather import store_today_weather


class Command(BaseCommand):
	help = '지수 수집 → 투자 날씨 산출 → 뉴스 섹터 갱신을 순차 실행합니다.'

	def handle(self, *args, **options):
		# 1. 시장 지수 수집 (코스피·코스닥)
		try:
			indices = collect_indices()
			self.stdout.write(self.style.SUCCESS(f"[1/3] 지수 수집 완료: {len(indices)}건"))
		except Exception as exc:
			self.stdout.write(self.style.ERROR(f"[1/3] 지수 수집 실패: {exc}"))

		# 2. 투자 날씨 산출
		try:
			weather = store_today_weather()
			if weather:
				self.stdout.write(self.style.SUCCESS(
					f"[2/3] 투자 날씨 산출 완료: {weather.weather_status}"
				))
			else:
				self.stdout.write(self.style.WARNING("[2/3] 지수 데이터가 없어 날씨를 산출하지 못했습니다."))
		except Exception as exc:
			self.stdout.write(self.style.ERROR(f"[2/3] 투자 날씨 산출 실패: {exc}"))

		# 3. 뉴스 섹터 카드뉴스 갱신 (기존 파이프라인)
		try:
			call_command('crawl_news')
			self.stdout.write(self.style.SUCCESS("[3/4] 뉴스 섹터 갱신 완료"))
		except Exception as exc:
			self.stdout.write(self.style.ERROR(f"[3/4] 뉴스 섹터 갱신 실패: {exc}"))

		# 4. 섹터별 대표 종목 조회·매핑 갱신 (API로 종목 확보)
		try:
			call_command('load_sector_stocks')
			self.stdout.write(self.style.SUCCESS("[4/4] 섹터 대표 종목 매핑 갱신 완료"))
		except Exception as exc:
			self.stdout.write(self.style.ERROR(f"[4/4] 섹터 대표 종목 매핑 갱신 실패: {exc}"))

		self.stdout.write(self.style.SUCCESS("daily_update 완료."))
