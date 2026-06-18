import pandas as pd
from django.core.management.base import BaseCommand
from tutors.models import Term

class Command(BaseCommand):
    help = '엑셀 파일에서 금융/경제 용어를 읽어 DB에 저장합니다.'

    def handle(self, *args, **options):
        # 1. 파일명만 간결하게 지정 (해당 파일이 manage.py와 같은 폴더에 있어야 합니다!)
        file_path = '../src/20260605_시사경제용어사전.xlsx'
        
        try:
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"'{file_path}' 파일을 찾을 수 없습니다. manage.py와 동일한 폴더에 파일이 있는지 확인해 주세요."))
            return

        # 2. '주제' 컬럼이 '금융'인 용어만 적재
        filtered_df = df[df['주제'] == '금융']

        terms_to_create = []
        # .dropna(subset=['용어', '설명']) 등을 추가해 빈 값이 들어가는 것을 방지하면 더 안전합니다.
        for index, row in filtered_df.dropna(subset=['용어', '설명']).iterrows():
            terms_to_create.append(
                Term(
                    term_name=str(row['용어']).strip(),
                    explanation=str(row['설명']).strip()
                )
            )
        
        Term.objects.bulk_create(terms_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"{len(terms_to_create)}개의 용어가 성공적으로 저장되었습니다."))