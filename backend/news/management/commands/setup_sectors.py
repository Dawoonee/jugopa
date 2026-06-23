"""섹터 시드 일괄 적재 — load_sectors → (대표 또는 전 종목) 매핑을 올바른 순서로 실행한다.

의존성(Sector 먼저, 그 다음 SectorStock 매핑)을 한 번에 처리하기 위한 편의 커맨드.
종목 매핑은 외부 데이터 소스가 필요하다:
- 기본(대표 ~5종목): load_sector_stocks — data.go.kr API 키 필요.
- --all-stocks(전 상장종목): load_all_sector_stocks — 네이버 업종 + FDR 사용. 이후 대표 매핑으로 rank 보강.
뉴스 수집/카드뉴스(crawl_news)는 시간에 의존적이라 별도로 실행한다.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	help = '섹터 분류표와 종목 매핑을 순서대로 적재합니다(load_sectors → 종목 매핑).'

	def add_arguments(self, parser):
		parser.add_argument(
			'--skip-stocks',
			action='store_true',
			help='종목 매핑을 건너뜁니다. (API 키 없이 섹터만 적재할 때)',
		)
		parser.add_argument(
			'--all-stocks',
			action='store_true',
			help='대표 종목 대신 전 상장종목을 적재하고(load_all_sector_stocks), '
				'대표 매핑으로 rank를 보강합니다.',
		)

	def handle(self, *args, **options):
		self.stdout.write('1/2) 섹터 분류표 적재 (load_sectors)...')
		call_command('load_sectors')

		if options['skip_stocks']:
			self.stdout.write(self.style.WARNING('2/2) 종목 매핑 건너뜀 (--skip-stocks).'))
			return

		if options['all_stocks']:
			self.stdout.write('2/2) 전 상장종목 적재 (load_all_sector_stocks)...')
			call_command('load_all_sector_stocks')
			self.stdout.write('   └ 대표 종목 rank 보강 (load_sector_stocks)...')
			call_command('load_sector_stocks')
		else:
			self.stdout.write('2/2) 대표 종목 매핑 적재 (load_sector_stocks)...')
			call_command('load_sector_stocks')

		self.stdout.write(self.style.SUCCESS('섹터 시드 적재 완료.'))
