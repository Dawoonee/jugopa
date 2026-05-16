import requests  # 1. requests 임포트 추가
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Stock, StockPriceDaily
from .serializers import StockSerializer, StockDetailSerializer

# Create your views here.
@api_view(['GET'])
def save_stocks(request):
    api_key = settings.FINANCIAL_API_KEY

    # 3. URL 슬래시(/) 추가 및 파라미터 중복 제거 (깔끔한 기본 URL만 남김)
    url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

    params = {
        'serviceKey': api_key,
        'resultType': 'json',
        'numOfRows': 100,
        'pageNo': 1,
    }

    try:
        # 2. request -> requests 로 수정
        response = requests.get(url, params=params)
        data = response.json()
        
        # 4. 빈 리스트([]) 대신 빈 딕셔너리({})로 수정하여 AttributeError 방지
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        def parse_to_int(value):
            if value is None or value == "":
                return -1
            try:
                return int(value)
            except ValueError:
                return -1

        for item in items:
            stock_code = item.get('srtnCd')     # 단축코드
            stock_name = item.get('itmsNm')     # 종목명
            market_type = item.get('mrktCtg')       # 시장구분

            stock, created = Stock.objects.get_or_create(
                stock_code=stock_code,
                defaults={'stock_name': stock_name, 'market_type': market_type}
            )

            bas_dt_str = item.get('basDt')
            if not bas_dt_str:
                continue
            
            try:
                record_date = datetime.strptime(bas_dt_str, '%Y%m%d').date()
            except ValueError:
                continue
            
            open_price = parse_to_int(item.get('mkp'))  # 시가
            close_price = parse_to_int(item.get('clpr'))  # 종가
            high_price = parse_to_int(item.get('hipr')) #고가
            low_price = parse_to_int(item.get('lopr')) #저가
            volume = parse_to_int(item.get('trqu')) # 거래량

            StockPriceDaily.objects.update_or_create(
                stock=stock,
                record_date=record_date,
                defaults={
                    'open_price':open_price,
                    'close_price': close_price,
                    'high_price':high_price,
                    'low_price':low_price,
                    'volume':volume,
                }
            )

        return Response({"message": "데이터가 성공적으로 수집 및 저장되었습니다. "}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"데이터 수집 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def stock_list_create(request):
    if request.method == 'GET':
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def stock_detail(request, stock_code):
    stock = get_object_or_404(Stock, stock_code=stock_code)
    serializer = StockDetailSerializer(stock)
    return Response(serializer.data)

@api_view(['GET'])
def top_performer(request):
    top_daily_record = StockPriceDaily.objects.order_by('-volume').first()

    if not top_daily_record:
        return Response({"error": "조회할 시세 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    top_stock = top_daily_record.stock
    serializer = StockDetailSerializer(top_stock)
    return Response(serializer.data)