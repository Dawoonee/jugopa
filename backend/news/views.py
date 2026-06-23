from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import SectorCardNews, Sector, SectorStock
from .serializers import SectorCardNewsSerializer, SectorSerializer
from .serializers import _stock_payload


@api_view(['GET'])
def sectors_list(request):
	"""관심 업종 선택 그리드용 — 활성 섹터(업종) 목록을 반환한다.

	?level=LARGE|MID 로 분류 단위를 지정한다(기본값 LARGE: 관심 섹터는 대분류만 선택).
	"""
	level = request.query_params.get('level', Sector.Level.LARGE)
	sectors = Sector.objects.filter(is_active=True)
	if level in (Sector.Level.LARGE, Sector.Level.MID):
		sectors = sectors.filter(level=level)
	sectors = sectors.order_by('display_order', 'name')
	return Response(SectorSerializer(sectors, many=True).data)


@api_view(['GET'])
def sector_stocks(request, sector_id):
	"""추천 화면 관심 업종 탭용 — 해당 섹터의 대표 종목 목록(최신 시세 포함).

	대분류(LARGE)가 들어오면 자식 중분류들의 SectorStock을 rank 순으로 집계한다.
	"""
	sector = get_object_or_404(Sector, pk=sector_id)
	if sector.level == Sector.Level.LARGE:
		links = SectorStock.objects.filter(sector__parent=sector)
	else:
		links = SectorStock.objects.filter(sector=sector)
	links = links.select_related('stock').order_by('-stock__market_cap')
	return Response({
		'sector_id': sector.id,
		'sector_name': sector.name,
		'stocks': [_stock_payload(link.stock) for link in links],
	})


@api_view(['GET'])
def card_news_detail(request, card_id):
	"""카드뉴스 상세 — 단건 카드뉴스 전문(본문·핵심포인트·원문기사·TOP 종목)을 반환한다."""
	card = get_object_or_404(
		SectorCardNews.objects.select_related('sector').prefetch_related('representative_articles'),
		pk=card_id,
	)
	return Response(SectorCardNewsSerializer(card).data)


@api_view(['GET'])
def sectors_today(request):
	"""주식 추천용 — 오늘자 추천 섹터 카드뉴스를 rank 순으로 반환한다.

	오늘자 데이터가 없으면 가장 최근 target_date 세트로 폴백한다.
	"""
	today = timezone.localdate()
	cards = SectorCardNews.objects.filter(target_date=today)
	if not cards.exists():
		latest = SectorCardNews.objects.order_by('-target_date').first()
		if latest:
			cards = SectorCardNews.objects.filter(target_date=latest.target_date)

	cards = cards.select_related('sector').prefetch_related('representative_articles').order_by('rank')
	serializer = SectorCardNewsSerializer(cards, many=True)
	return Response(serializer.data)
