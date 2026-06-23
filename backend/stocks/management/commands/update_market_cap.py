import time
from django.core.management.base import BaseCommand
from stocks.models import Stock
from stocks.stock_fetcher import fetch_stock_by_name

class Command(BaseCommand):
    help = "기존 종목의 시가총액 데이터를 업데이트합니다."

    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        total = stocks.count()
        self.stdout.write(f"총 {total}개 종목 시가총액 업데이트 시작...")

        updated_count = 0
        for i, stock in enumerate(stocks, 1):
            # API에 부하를 주지 않기 위해 지연
            time.sleep(0.1)
            
            # fetch_stock_by_name은 내부적으로 최신 mrktTotAmt를 가져와 
            # Stock 모델의 market_cap을 갱신(upsert)합니다.
            result = fetch_stock_by_name(stock.stock_name)
            
            if result and result.market_cap > 0:
                self.stdout.write(f"[{i}/{total}] {stock.stock_name} 시가총액 업데이트 완료: {result.market_cap:,}")
                updated_count += 1
            else:
                self.stdout.write(f"[{i}/{total}] {stock.stock_name} 조회 실패 또는 시가총액 없음")

        self.stdout.write(self.style.SUCCESS(f"업데이트 완료. 총 {updated_count}/{total}개 갱신됨."))
