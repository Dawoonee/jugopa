"""섹터별 대표 종목을 API로 조회해 Stock을 확보하고 SectorStock 매핑을 적재한다.

각 대표 종목명을 data.go.kr 주식시세정보 API(likeItmsNm)로 조회하므로,
DB에 없던 종목도 새로 적재된다(API 키 사용). 실행 전 `load_sectors`로 Sector가 있어야 한다.
"""

from django.core.management.base import BaseCommand

from news.models import Sector, SectorStock
from news.sector_stocks_seed import SECTOR_STOCKS
from stocks.stock_fetcher import fetch_stock_by_name


class Command(BaseCommand):
	help = '섹터별 대표 종목을 API로 조회·적재하고 SectorStock 매핑을 갱신합니다.'

	def handle(self, *args, **options):
		created = 0
		failed = 0
		for sector_name, stock_names in SECTOR_STOCKS.items():
			sector = Sector.objects.filter(name=sector_name).first()
			if not sector:
				self.stdout.write(self.style.WARNING(f"섹터 없음: {sector_name} (load_sectors 먼저 실행)"))
				continue

			for rank, stock_name in enumerate(stock_names):
				stock = fetch_stock_by_name(stock_name)
				if not stock:
					failed += 1
					self.stdout.write(self.style.WARNING(f"  조회 실패: {sector_name} - {stock_name}"))
					continue
				SectorStock.objects.update_or_create(
					sector=sector, stock=stock, defaults={'rank': rank},
				)
				created += 1

			self.stdout.write(f"  {sector_name}: 매핑 갱신")

		self.stdout.write(self.style.SUCCESS(
			f"SectorStock 적재 완료: 매핑 {created}건 / 조회 실패 {failed}건"
		))
