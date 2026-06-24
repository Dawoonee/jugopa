"""코스피·코스닥 상장 전 종목을 수집해 28개 중분류에 분류·적재한다.

데이터 소스:
- 분류: 네이버 금융 '업종분류'(GICS 79업종) → news/naver_sector_map 으로 WICS 28중분류 변환.
- 시세/시총: FinanceDataReader(KRX 상장 전 종목)로 종가·시가총액을 받아 Stock/StockPriceDaily/rank에 사용.

실행 전 `load_sectors`로 28개 중분류 Sector가 있어야 한다. 섹터 내 rank는 시가총액 내림차순.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from news.models import Sector, SectorStock
from news.naver_sector_map import map_naver_to_wics
from stocks import sector_universe
from stocks.index_collector import latest_trading_date
from stocks.models import Stock, StockPriceDaily


class Command(BaseCommand):
	help = '상장 전 종목을 네이버 업종 분류 + FDR 시세로 28개 중분류에 적재합니다.'

	def add_arguments(self, parser):
		parser.add_argument(
			'--market', choices=['KOSPI', 'KOSDAQ'], action='append',
			help='수집 시장(반복 지정 가능). 미지정 시 코스피+코스닥 모두.',
		)
		parser.add_argument(
			'--dry-run', action='store_true',
			help='DB에 적재하지 않고 분류 통계만 출력합니다.',
		)

	def handle(self, *args, **options):
		markets = tuple(options['market']) if options['market'] else sector_universe.MARKETS
		sectors = self._load_sectors_or_fail()
		if sectors is None:
			return

		self.stdout.write(f"시장 {', '.join(markets)} - 수집 시작...")
		listing = sector_universe.fetch_listing(markets)
		membership = sector_universe.fetch_sector_membership()
		self.stdout.write(f"  상장 종목 {len(listing)}개 / 네이버 업종 매핑 {len(membership)}개")

		classified, unmapped, missing = self._classify(listing, membership, sectors)

		if options['dry_run']:
			self._report(classified, unmapped, missing, persisted=False)
			return

		self._persist(classified)
		self._report(classified, unmapped, missing, persisted=True)

	def _load_sectors_or_fail(self):
		mids = {s.name: s for s in Sector.objects.filter(level=Sector.Level.MID)}
		if not mids:
			self.stdout.write(self.style.ERROR(
				"중분류 Sector가 없습니다. 먼저 `python manage.py load_sectors`를 실행하세요."
			))
			return None
		return mids

	def _classify(self, listing, membership, sectors):
		"""종목을 중분류로 분류한다.

		반환:
		- classified: {중분류명: [(code, info), ...]}
		- unmapped: {네이버업종명: 종목수}  (매핑 사전에 없는 업종)
		- missing_listing: 업종엔 있지만 FDR 시세에 없는 종목 수
		"""
		classified = {}
		unmapped = {}
		missing_listing = 0
		for code, industry in membership.items():
			info = listing.get(code)
			if not info:
				missing_listing += 1
				continue
			mid_name = map_naver_to_wics(industry)
			if not mid_name or mid_name not in sectors:
				unmapped[industry] = unmapped.get(industry, 0) + 1
				continue
			classified.setdefault(mid_name, []).append((code, info))
		return classified, unmapped, missing_listing

	@transaction.atomic
	def _persist(self, classified):
		"""Stock/시총/시세 upsert 후 섹터별 시총 내림차순 rank로 SectorStock을 갱신한다."""
		sectors = {s.name: s for s in Sector.objects.filter(level=Sector.Level.MID)}
		# 시세 기준일을 지수와 통일: 최신 시장 지수 기준일(실제 거래일). 지수 미수집 시에만 실행일 폴백.
		record_date = latest_trading_date() or timezone.localdate()
		for mid_name, rows in classified.items():
			sector = sectors[mid_name]
			rows.sort(key=lambda r: r[1]['marcap'], reverse=True)
			for rank, (code, info) in enumerate(rows):
				stock, _ = Stock.objects.update_or_create(
					stock_code=code,
					defaults={
						'stock_name': info['name'],
						'market_type': info['market'],
						'market_cap': info['marcap'],
					},
				)
				if info['close']:
					StockPriceDaily.objects.update_or_create(
						stock=stock, record_date=record_date,
						defaults={
							'open_price': info['open'],
							'close_price': info['close'],
							'high_price': info['high'],
							'low_price': info['low'],
							'volume': info['volume'],
						},
					)
				SectorStock.objects.update_or_create(
					sector=sector, stock=stock, defaults={'rank': rank},
				)

	def _report(self, classified, unmapped, missing_listing, persisted):
		total = sum(len(v) for v in classified.values())
		self.stdout.write("== 중분류별 분류 결과 ==")
		for name in sorted(classified, key=lambda n: -len(classified[n])):
			self.stdout.write(f"  {name}: {len(classified[name])}개")

		empty = [
			s.name for s in Sector.objects.filter(level=Sector.Level.MID)
			if s.name not in classified
		]
		if empty:
			self.stdout.write(self.style.WARNING(
				f"비어있는 중분류 {len(empty)}개: {', '.join(empty)}"
			))
		if unmapped:
			detail = ', '.join(f"{k}({v})" for k, v in sorted(unmapped.items(), key=lambda kv: -kv[1]))
			self.stdout.write(self.style.WARNING(f"미매핑 업종(사전 보강 대상): {detail}"))
		if missing_listing:
			self.stdout.write(self.style.WARNING(
				f"FDR 시세에 없는 종목 {missing_listing}개(상폐/우선주/ETN 등) — 적재 제외"
			))

		verb = "적재" if persisted else "분류(dry-run, 미적재)"
		self.stdout.write(self.style.SUCCESS(
			f"{verb} 완료: 종목 {total}건 / 중분류 {len(classified)}개"
		))
