from django.core.management.base import BaseCommand

from news.models import Sector
from news.sectors_seed import LARGE_SECTORS, MID_SECTORS


class Command(BaseCommand):
	help = 'WICS 섹터 분류표(대분류 10/중분류 28)를 DB에 계층 구조로 적재합니다.'

	def handle(self, *args, **options):
		large_count = self._load_large()
		mid_count = self._load_mid()

		self.stdout.write(self.style.SUCCESS(
			f"섹터 적재 완료: 대분류 {large_count}개 / 중분류 {mid_count}개 "
			f"(총 {Sector.objects.count()}개)."
		))

	def _load_large(self):
		"""대분류를 먼저 적재한다(parent=None)."""
		count = 0
		for order, name in enumerate(LARGE_SECTORS):
			Sector.objects.update_or_create(
				name=name,
				level=Sector.Level.LARGE,
				defaults={
					'parent': None,
					'keywords': [],
					'display_order': order,
					'is_active': True,
				},
			)
			count += 1
		return count

	def _load_mid(self):
		"""중분류를 대분류 FK와 함께 적재한다."""
		count = 0
		order = 0
		for large_name, mids in MID_SECTORS.items():
			parent = Sector.objects.get(name=large_name, level=Sector.Level.LARGE)
			for mid_name, keywords in mids:
				Sector.objects.update_or_create(
					name=mid_name,
					level=Sector.Level.MID,
					defaults={
						'parent': parent,
						'keywords': keywords,
						'display_order': order,
						'is_active': True,
					},
				)
				order += 1
				count += 1
		return count
