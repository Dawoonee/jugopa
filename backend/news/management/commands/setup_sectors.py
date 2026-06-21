"""섹터 시드 일괄 적재 — load_sectors → load_sector_stocks를 올바른 순서로 실행한다.

의존성(Sector 먼저, 그 다음 SectorStock 매핑)을 한 번에 처리하기 위한 편의 커맨드.
종목 시세 API(load_sector_stocks)는 data.go.kr API 키가 필요하다.
뉴스 수집/카드뉴스(crawl_news)는 시간에 의존적이라 별도로 실행한다.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	help = '섹터 분류표와 대표 종목 매핑을 순서대로 적재합니다(load_sectors → load_sector_stocks).'

	def add_arguments(self, parser):
		parser.add_argument(
			'--skip-stocks',
			action='store_true',
			help='대표 종목 매핑(load_sector_stocks)을 건너뜁니다. (API 키 없이 섹터만 적재할 때)',
		)

	def handle(self, *args, **options):
		self.stdout.write('1/2) 섹터 분류표 적재 (load_sectors)...')
		call_command('load_sectors')

		if options['skip_stocks']:
			self.stdout.write(self.style.WARNING('2/2) 대표 종목 매핑 건너뜀 (--skip-stocks).'))
			return

		self.stdout.write('2/2) 대표 종목 매핑 적재 (load_sector_stocks)...')
		call_command('load_sector_stocks')

		self.stdout.write(self.style.SUCCESS('섹터 시드 적재 완료.'))
