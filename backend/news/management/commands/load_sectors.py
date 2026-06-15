from django.core.management.base import BaseCommand

from news.models import Sector
from news.sectors_seed import SECTORS


class Command(BaseCommand):
    help = '고정 섹터 분류표(sectors_seed)를 DB에 적재합니다.'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for order, (name, keywords) in enumerate(SECTORS):
            _, was_created = Sector.objects.update_or_create(
                name=name,
                defaults={
                    'keywords': keywords,
                    'display_order': order,
                    'is_active': True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"섹터 적재 완료: 신규 {created}개, 갱신 {updated}개 (총 {Sector.objects.count()}개)."
        ))
