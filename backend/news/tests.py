import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Sector, SectorStock, SectorCardNews, NewsArticle
from stocks.models import Stock
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def large_sector():
    return Sector.objects.create(
        name="IT", level=Sector.Level.LARGE, display_order=1, is_active=True
    )

@pytest.fixture
def test_sector(large_sector):
    """카드뉴스/매핑 단위인 중분류(MID). 대분류 IT를 부모로 둔다."""
    return Sector.objects.create(
        name="반도체와 반도체장비", level=Sector.Level.MID,
        parent=large_sector, display_order=1, is_active=True,
    )

@pytest.fixture
def test_stock():
    return Stock.objects.create(stock_code="005930", stock_name="삼성전자", market_type="KOSPI")

@pytest.fixture
def test_sector_stock(test_sector, test_stock):
    return SectorStock.objects.create(sector=test_sector, stock=test_stock, rank=1)

@pytest.fixture
def test_card_news(test_sector):
    today = timezone.localdate()
    return SectorCardNews.objects.create(
        sector=test_sector,
        target_date=today,
        headline="IT News Headline",
        summary="IT Summary",
        rank=1
    )

@pytest.mark.django_db
class TestNewsAPI:
    def test_sectors_list_defaults_to_large(self, api_client, large_sector, test_sector):
        """관심 섹터 선택용 — 기본은 대분류(LARGE)만 반환한다."""
        url = reverse('news:sectors_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        names = [s['name'] for s in response.data]
        assert "IT" in names                       # 대분류
        assert "반도체와 반도체장비" not in names    # 중분류는 제외

    def test_sectors_list_mid(self, api_client, large_sector, test_sector):
        url = reverse('news:sectors_list')
        response = api_client.get(url, {'level': 'MID'})
        assert response.status_code == status.HTTP_200_OK
        names = [s['name'] for s in response.data]
        assert "반도체와 반도체장비" in names
        assert "IT" not in names

    def test_sectors_today(self, api_client, test_card_news):
        url = reverse('news:sectors_today')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['headline'] == "IT News Headline"

    def test_card_news_detail(self, api_client, test_card_news):
        url = reverse('news:card_news_detail', kwargs={'card_id': test_card_news.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['headline'] == "IT News Headline"

    def test_sector_stocks(self, api_client, test_sector, test_sector_stock):
        url = reverse('news:sector_stocks', kwargs={'sector_id': test_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['sector_id'] == test_sector.id
        assert len(response.data['stocks']) >= 1
        assert response.data['stocks'][0]['stock_code'] == "005930"

    def test_sector_stocks_large_aggregates_children(
        self, api_client, large_sector, test_sector, test_sector_stock
    ):
        """대분류 id로 조회하면 자식 중분류들의 매핑을 집계해 반환한다."""
        url = reverse('news:sector_stocks', kwargs={'sector_id': large_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        codes = [s['stock_code'] for s in response.data['stocks']]
        assert "005930" in codes


@pytest.mark.django_db
class TestLoadSectors:
    def test_load_sectors_seeds_hierarchy(self):
        from django.core.management import call_command
        call_command('load_sectors')

        assert Sector.objects.filter(level=Sector.Level.LARGE).count() == 10
        assert Sector.objects.filter(level=Sector.Level.MID).count() == 28
        # 모든 중분류는 대분류 부모를 가진다
        orphan_mid = Sector.objects.filter(
            level=Sector.Level.MID, parent__isnull=True
        ).count()
        assert orphan_mid == 0
