from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from .models import SectorCardNews, Sector
from .serializers import SectorCardNewsSerializer, SectorSerializer


@api_view(['GET'])
def sectors_list(request):
	"""관심 업종 선택 그리드용 — 활성 섹터(업종) 목록을 반환한다."""
	sectors = Sector.objects.filter(is_active=True).order_by('display_order', 'name')
	return Response(SectorSerializer(sectors, many=True).data)


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
