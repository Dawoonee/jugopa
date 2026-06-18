import requests  # 1. requests 임포트 추가
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Stock, StockPriceDaily, MarketIndexDaily, DailyMarketWeather, UserBookmark
from .serializers import (
    StockSerializer, StockDetailSerializer,
    MarketIndexDailySerializer, DailyMarketWeatherSerializer,
    UserBookmarkSerializer,
)
from .index_collector import TARGET_INDICES
from .stock_fetcher import fetch_price_history, fetch_stock_by_name

# 상세 페이지 시세 그래프 일수 / 신선도 가드 기준
PRICE_HISTORY_DAYS = 30
PRICE_FRESHNESS_MIN_COUNT = 20
PRICE_FRESHNESS_WINDOW_DAYS = 40

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
def stock_search(request):
    """종목명으로 검색 — 로컬 DB 우선, 없으면 공공API(likeItmsNm) 폴백 적재 후 반환한다."""
    query = (request.query_params.get('q') or '').strip()
    if not query:
        return Response([])

    matches = Stock.objects.filter(stock_name__icontains=query)[:10]
    if not matches:
        fetched = fetch_stock_by_name(query)
        matches = [fetched] if fetched else []

    serializer = StockSerializer(matches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def stock_detail(request, stock_code):
    stock = get_object_or_404(Stock, stock_code=stock_code)

    # 신선도 가드: 최근 윈도우 내 시세가 부족하면 공공API로 30일치 백필(첫 로드만 외부호출).
    window_start = datetime.now().date() - timedelta(days=PRICE_FRESHNESS_WINDOW_DAYS)
    recent_count = stock.daily_prices.filter(record_date__gte=window_start).count()
    if recent_count < PRICE_FRESHNESS_MIN_COUNT:
        fetch_price_history(stock_code, PRICE_HISTORY_DAYS)

    serializer = StockDetailSerializer(stock, context={'price_limit': PRICE_HISTORY_DAYS})
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bookmarks(request):
    """관심 종목 — GET: 내 목록 조회 / POST: 추가(body: stock_code)."""
    if request.method == 'GET':
        qs = UserBookmark.objects.filter(user=request.user).select_related('stock').order_by('-created_at')
        return Response(UserBookmarkSerializer(qs, many=True).data)

    stock_code = request.data.get('stock_code')
    stock = get_object_or_404(Stock, stock_code=stock_code)
    bookmark, created = UserBookmark.objects.get_or_create(user=request.user, stock=stock)
    serializer = UserBookmarkSerializer(bookmark)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bookmark_delete(request, stock_code):
    """관심 종목 해제."""
    deleted, _ = UserBookmark.objects.filter(user=request.user, stock__stock_code=stock_code).delete()
    if not deleted:
        return Response({"detail": "관심 종목에 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def market_indices(request):
    """홈 대시보드용 — 대상 시장지수(코스피·코스닥·코스피200·KRX300)의 최신값을 반환한다."""
    indices = []
    for index_name in TARGET_INDICES:
        latest = MarketIndexDaily.objects.filter(index_name=index_name).first()
        if latest:
            indices.append(latest)
    serializer = MarketIndexDailySerializer(indices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def market_weather_today(request):
    """홈 대시보드용 — 오늘자 투자 날씨(없으면 최신 1건)를 반환한다."""
    today = datetime.now().date()
    weather = DailyMarketWeather.objects.filter(target_date=today).first()
    if not weather:
        weather = DailyMarketWeather.objects.order_by('-target_date').first()
    if not weather:
        return Response({"detail": "산출된 투자 날씨가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    serializer = DailyMarketWeatherSerializer(weather)
    return Response(serializer.data)


@api_view(['GET'])
def top_performer(request):
    top_daily_record = StockPriceDaily.objects.order_by('-volume').first()

    if not top_daily_record:
        return Response({"error": "조회할 시세 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    top_stock = top_daily_record.stock
    serializer = StockDetailSerializer(top_stock)
    return Response(serializer.data)