import pandas as pd
from django.core.management.base import BaseCommand
from tutors.models import Term

class Command(BaseCommand):
    help = '엑셀 파일에서 금융/경제 용어를 읽어 DB에 저장합니다.'

    def handle(self, *args, **options):
        file_path = '../../../src/20260605_시사경제용어사전.xlsx'
        # 실제 파일명으로 변경 필요
        
        try:
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("엑셀 파일을 찾을 수 없습니다."))
            return

        # '금융/경제' 카테고리만 필터링
        filtered_df = df[df['카테고리'] == '금융/경제']

        terms_to_create = []
        for index, row in filtered_df.iterrows():
            terms_to_create.append(
                Term(
                    term_name=row['용어명'],
                    explanation=row['설명']
                )
            )
        
        Term.objects.bulk_create(terms_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"{len(terms_to_create)}개의 용어가 성공적으로 저장되었습니다."))