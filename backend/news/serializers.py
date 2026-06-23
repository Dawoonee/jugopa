from rest_framework import serializers

from .models import NewsArticle, SectorCardNews, Sector, SectorStock
from stocks.models import StockPriceDaily


class SectorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Sector
		fields = ['id', 'name', 'display_order']


class RepresentativeArticleSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewsArticle
		fields = ['title', 'link', 'source', 'published_at']


def _latest_price(stock):
	"""종목의 최신 일별 시세(종가/등락 산출용)를 반환. 없으면 None."""
	return StockPriceDaily.objects.filter(stock=stock).order_by('-record_date').first()


def _stock_payload(stock):
	"""TOP 종목 게이지용 종목 정보(코드·이름·종가·등락률)."""
	price = _latest_price(stock)
	change_rate = None
	if price and price.open_price:
		change_rate = round((price.close_price - price.open_price) / price.open_price * 100, 2)
	return {
		'stock_code': stock.stock_code,
		'stock_name': stock.stock_name,
		'close_price': price.close_price if price else None,
		'change_rate': change_rate,
	}


class SectorCardNewsSerializer(serializers.ModelSerializer):
	sector_name = serializers.SerializerMethodField()
	representative_articles = RepresentativeArticleSerializer(many=True, read_only=True)
	top_stocks = serializers.SerializerMethodField()

	def get_sector_name(self, obj):
		# 카드뉴스는 중분류(MID) 단위로 생성되므로 중분류 이름을 그대로 노출한다.
		# (대분류로 묶으면 같은 대분류의 중분류 여러 건이 동일 이름으로 중복 표시됨)
		return obj.sector.name if obj.sector else ''

	class Meta:
		model = SectorCardNews
		fields = [
			'id', 'rank', 'sector_name', 'target_date', 'headline', 'summary',
			'key_points', 'article_count', 'representative_articles', 'top_stocks',
		]

	def get_top_stocks(self, obj):
		"""섹터 매핑(SectorStock) rank 순 최대 3종목. 매핑이 없으면 거래량 상위로 폴백."""
		links = SectorStock.objects.filter(sector=obj.sector).select_related('stock').order_by('rank')[:3]
		stocks = [link.stock for link in links]
		if not stocks:
			# 폴백: 최신 거래량 상위 3종목
			top_prices = StockPriceDaily.objects.select_related('stock').order_by('-volume')[:3]
			seen = set()
			for price in top_prices:
				if price.stock_id not in seen:
					stocks.append(price.stock)
					seen.add(price.stock_id)
		return [_stock_payload(s) for s in stocks]
